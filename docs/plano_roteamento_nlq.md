# Plano: roteamento solo queue × profissional na consulta em linguagem natural

Escrito em 2026-11-04 (noite). Entrega em 16/11/2026. **Nada aqui foi executado.**
Este plano vem antes de continuar as correções das respostas de SQL (ver
`docs/revisao_nlq_incertas.md`).

## 1. O problema

O sistema tem **duas bases paralelas** com convenções diferentes, e uma caixa de
pergunta só:

| | Solo queue | Profissional |
|---|---|---|
| Tabelas | `matches`, `teams`, `participants`, `players`, `bans`, `item_events`, `items` | `pro_games`, `pro_players` |
| Lado | `team_id` 100 / 200 | `side` 'Blue' / 'Red' |
| Posição | MAIÚSCULAS (`MIDDLE`) | minúsculas (`mid`) |
| Campeão | `champion_name` interno | nome de exibição, com espaço |
| Nome de equipe e jogador | não existe / `NULL` | `team_name`, `player_name` |
| Ano, liga, patch | só `game_creation`, `game_version` | `year`, `league`, `patch` |

Nas 50 perguntas livres, 7 foram respondidas sem que o sistema soubesse (nem dissesse)
de qual base falava (3, 7, 8, 9, 10, 15, 38), e outras 5 caíram em tabela errada ou
mistura de bases (10, 38, 40...). O benchmark de 26 perguntas **não mostrava isso**:
as 4 perguntas do profissional dizem "profissionais" ou "no competitivo". A ambiguidade
só aparece com perguntas livres.

Causa: é falha de organização, não só do modelo. A interface não explicita a base, o
esquema mistura as duas no mesmo prompt, e o sistema nunca declara o que assumiu.

## 2. Objetivo e o que NÃO muda

**Objetivo:** toda resposta diz de qual base veio; pergunta ambígua devolve as duas
respostas, rotuladas; o modelo nunca mistura as bases numa mesma consulta.

**Não muda (invariantes do AGENTS.md):**
- `validate_sql` e as três camadas de `sql_guard.py`: nenhuma regra afrouxada.
- `temperature=0` e `max_tokens=1200` na geração da SQL.
- `SqlExecutionError` carrega SQL e causa, e não engole o erro.
- `evaluate_nlq` continua medindo a geração direta (23/26 -> 26/26 já registrado);
  o benchmark não é editado.
- Número no TCC só vem de artefato.
- Corpo do TCC em 29 páginas (limite 30).

## 3. Desenho

### 3.1 Três classes

`SOLO`, `PRO` e `AMBOS`. **AMBOS** cobre duas situações com o mesmo tratamento: a pergunta
não dá pista, ou pede as duas bases ("compare o viés de lado no solo queue e no
profissional").

### 3.2 Pistas (regras explícitas, em código, testáveis)

| Indica PRO | Indica SOLO |
|---|---|
| equipe, time com nome, liga, temporada, split, playoffs, patch, torneio, LCK/LPL/LEC/... , profissional, competitivo, jogador pelo nome | time azul/vermelho (sem nome), ranqueada, solo queue, elo, challenger/grandmaster/master, posição em MAIÚSCULAS (TOP, JUNGLE, MIDDLE, BOTTOM/ADC, UTILITY/SUPPORT), itens, banimentos |

Conflito (pistas dos dois lados) ou ausência de pista: vai para o classificador de
linguagem (passo 3.3). Se ele devolver algo fora do conjunto `{SOLO, PRO, AMBOS}`,
**trata como AMBOS** (nunca confia em saída malformada).

### 3.3 Dois passos

1. **Roteador.** Primeiro as regras de código (determinísticas, sem custo). Só o resíduo
   vai para uma chamada curta a Haiku (`temperature=0`, `max_tokens` pequeno, com
   conferência de `stop_reason`, lição de `nl_to_sql`). A saída só escolhe a dica.
2. **Geração.** `generate_sql(question, history, base=...)` coloca a dica na mensagem
   do usuário (o esquema no prompt de sistema fica igual, e o benchmark não muda):
   "Use somente as tabelas do solo queue" ou "Use somente pro_games e pro_players".
   Em AMBOS, duas gerações, uma por base.

### 3.4 Guarda de base (determinística)

Depois de `validate_sql`, uma checagem nova: as tabelas da SQL têm de estar **só** na base
pedida. Mistura (como `teams` junto com `pro_games` na pergunta 40) é tratada como erro
de execução: entra na nova tentativa, com a mensagem "você usou tabela da outra base".
Reaproveita o analisador de `sql_guard.py` (`_referenced_tables`).

### 3.5 Contrato da resposta

```
{ "base": "solo" | "competitivo" | "ambos",
  "resultados": [ { "base": ..., "sql": ..., "columns": [...], "rows": [...],
                    "tentativas": 1|2, "erro": null | {"message","sql","cause"} } ],
  # compatibilidade temporária: sql/columns/rows = resultados[0]
}
```

- Em AMBOS, se uma base falha ou recusa ("não é possível responder"), a outra aparece, e
  a recusa/erro aparece rotulado: ela informa (ex.: pentakill não existe em nenhuma base).
- Todas falham: `SqlExecutionError` da última, como hoje (HTTP 422).
- **Continuação de conversa:** cada turno guarda a(s) base(s). O roteador recebe a base
  do turno anterior e a mantém, a não ser que a nova pergunta traga pista contrária.
  Se o turno anterior foi AMBOS, a continuação é roteada de novo.
- **Explicação** (`/ask/explain`): continua por resultado, pedida sob demanda na aba
  (não dobra o custo quando a pergunta é ambígua).

### 3.6 Interface

- Selo "Solo queue" ou "Competitivo" em cada resultado.
- Em AMBOS, dois painéis lado a lado (ou abas, ver decisão D3), cada um com SQL e
  Explicação como hoje.
- Dica sob a caixa: "diga 'no competitivo' ou 'no solo queue' para escolher a base".
- `AskResult` em `api.ts` e o histórico de `Nlq.tsx` mudam; o teste de fumaça das páginas
  cobre a tela.

## 4. Fases

| Fase | O que entra | Pronto quando |
|---|---|---|
| **0. Decisões** | Pistas, contrato, AMBOS, continuação de conversa, interface (seção 8) | Você aprova D1 a D6 |
| **1. Roteador** | `src/nlq/route.py` (regras + chamada curta), `tests/test_route.py` | Tabela de frases com classe esperada passa; saída inválida vira AMBOS; sem chamada de API nos testes (falsos) |
| **2. Geração com base** | `generate_sql(..., base=)`, guarda de base, nova tentativa citando a base | `tests/test_ask_base.py` com falsos; `evaluate_nlq` segue em 26/26 |
| **3. Orquestração** | `ask()` devolve `resultados`; AMBOS roda duas bases; falha parcial | Cenários de teste: clara, ambígua, uma recusa, uma falha, as duas falham, continuação |
| **4. API e tela** | `/ask` com o contrato novo, `Nlq.tsx`, `api.ts` | `npm run lint`, `test`, `build` verdes; demonstração manual das duas formas |
| **5. Medição** | Conjunto de roteamento com rótulos por pista; `evaluate_nlq --produto` (usa `ask`); 50 perguntas de novo | Artefato em `reports/` e quadro no Apêndice B |
| **6. Documentação e TCC** | Seção 4.7, 5.6, 6.1, Apêndice B; guia; comandos; scripts; handoff; checagem | `verifica_tcc` e `confere_docx` verdes, corpo em 29 páginas |

## 5. Como vamos medir

1. **Roteamento.** Rótulo por pista, não por intenção (a intenção de quem perguntou não é
   recuperável). Pergunta com pista -> a classe da pista; sem pista -> AMBOS. Base de
   teste: as 26 do benchmark (22 SOLO, 4 PRO) mais as 50 livres. Eu proponho os rótulos
   e você revisa só os discutíveis (cerca de 10 minutos).
2. **Produto.** `evaluate_nlq --produto` roda as 26 pelo `ask()` com o roteador e compara
   o resultado da base escolhida com a SQL de referência. Meta: **não regredir** do que a
   geração direta já faz (26/26). Mede o que o usuário vê.
3. **Pontuação das ambíguas.** Certa se declarar a base ou devolver as duas e cada uma
   estiver correta. Errada se escolher uma em silêncio. Hoje nenhuma ambígua declara.
4. **As 50 livres de novo**, com folha de revisão. As 50 **já estão contaminadas** (vi
   todas as respostas), então não servem como nota cega.
5. **Nota cega:** conjunto novo de 20 a 25 perguntas escritas por outras pessoas, julgado
   por você. É o único número que vai ao Resumo.

## 6. Riscos

| Risco | Mitigação |
|---|---|
| Roteador erra e manda para a base errada em silêncio | Selo de base sempre visível; AMBOS no caso de dúvida; roteamento medido |
| Mais uma chamada: custo e latência | Regras de código primeiro, a chamada só no resíduo; Haiku; ambíguas somam 3 chamadas |
| Rótulo "AMBOS" demais e a tela fica poluída | Medir a taxa de AMBOS nas 76 perguntas; se passar de ~40%, refinar as pistas |
| Conversa de continuação complexa | Base herdada do turno anterior, com teste por cenário |
| Eu ajustar as pistas olhando as 50 | Pistas são geradas das regras do esquema (documentadas), e a nota final vem do conjunto cego |
| Página do corpo | Uma frase na 4.7 e o resultado no Apêndice B; corte equivalente se precisar |
| Mudar API quebra a tela | Campos antigos mantidos como cópia de `resultados[0]` até a tela migrar |

## 7. Cronograma (entrega em 16/11)

| Dia | O que |
|---|---|
| 5/11 (qui) | Fase 0 (decisões) e Fase 1 (roteador, testes, rótulos) |
| 6/11 | Fases 2 e 3 (geração com base, guarda de base, orquestração) |
| 7/11 | Fase 4 (API e tela) e demonstração manual |
| 8/11 | Fase 5: `evaluate_nlq --produto` e as 50 de novo. **Você precisa ter entregue as 20 a 25 perguntas novas até hoje** |
| 9/11 | Melhorias gerais do esquema que ficaram pendentes: `NULLS LAST` e filtro de nulo na ordenação decrescente, recusar quando falta a coluna, top por grupo; depois a nota cega |
| 10 a 11/11 | Fase 6: texto, guia, checagem, commits |
| 12 a 13/11 | Folga e releitura |
| 14 a 15/11 | Ensaio da defesa |

## 8. Decisões que dependem de você

- **D1.** AMBOS = responder as duas bases, rotuladas (e não escolher uma, nem perguntar de volta).
- **D2.** Roteador em duas camadas: regras de código primeiro e uma chamada curta só no resíduo.
- **D3.** Interface: dois painéis lado a lado ou abas (recomendo painéis, para ver o contraste).
- **D4.** Continuação de conversa herda a base do turno anterior.
- **D5.** Onde registrar no TCC: uma frase na 4.7 e o resultado no Apêndice B.
- **D6.** Conjunto cego: você consegue as 20 a 25 perguntas até 8/11 e julga os resultados.

## 9. O que fica explicitamente fora

- Melhorias do esquema que não sejam do roteamento (ficam para depois, no dia 9).
- Mudar `validate_sql`, o benchmark ou a temperatura.
- Interface de pergunta de esclarecimento ("você quer solo ou profissional?").
- Qualquer commit sem você pedir.

## 10. Status (2026-11-04, noite)

- **Fase 1 feita:** `src/nlq/route.py` e `tests/test_route.py`. As regras decidiram
  corretamente as 16 perguntas do benchmark que decidiram (12 solo, 4 competitivo);
  resíduo de 10 de 26 e 16 de 50. Achado ao vivo: o modelo às vezes responde a palavra
  e segue explicando; o leitor passou a aceitar só a primeira linha (teste novo).
- **Fase 2 feita:** `generate_sql(..., base=)`, `sql_guard.validate_base` (guarda de
  mistura de bases) e `ask_base`, com a nova tentativa citando a mistura
  (`tests/test_ask_base.py`).
- **Fase 3 feita:** `ask()` roteia e roda uma ou as duas bases; uma base que falha não
  derruba a outra; se todas falham, levanta a última (`tests/test_ask_route.py`).
- **Fase 4 feita:** `/ask` devolve `roteamento`, `base` e `resultados` (campos antigos
  mantidos) e a tela mostra o selo da base e os dois painéis (`tests/test_api_ask.py`,
  `Nlq.test.tsx`; lint, 37 testes e build verdes).
- **Verificação ao vivo:** "Qual lado do mapa apresentou a maior taxa de vitória?"
  devolve solo (vermelho 53,3%) e competitivo (azul 53,2%).
- `evaluate_nlq` segue em 26/26 (geração direta, sem roteamento).
- **Falta:** Fase 5 (medição: `evaluate_nlq --produto`, as 50 de novo, conjunto cego) e
  Fase 6 (texto do TCC, guia, comandos, checagem). Nada commitado.

## 11. Status da Fase 5 (2026-11-05)

- **Conjunto cego recebido** (50 perguntas, `docs/nlq_perguntas_cegas.txt`, numeradas 51 a
  100). Eu vi o TEXTO das perguntas antes de congelar; **não vi nenhum resultado**.
- **Regras gerais de esquema aplicadas antes de congelar** (derivadas das 50 de
  desenvolvimento e das colunas reais do banco): nulos no fim do ranking, "o X de cada Y"
  com ROW_NUMBER, lista do que o schema NÃO tem (pentakill, "primeiro X", ouro/CS/dano/
  banimento no competitivo) e, depois da falha da 33 do desenvolvimento, um exemplo de
  recusa de "ouro total da equipe no competitivo". Disclosure: esse exemplo toca em um
  tema que o conjunto cego também sonda (ouro e CS totais de equipe).
- **Regressão:** `evaluate_nlq` 26/26 (25/26 numa passada, na família conhecida
  "coluna de contagem a mais"; reforcei a regra do limiar e voltou a 26/26).
- **Desenvolvimento, última passada:** 48 de 50 responderam, 2 erros (46 e 49, consultas
  complexas), 8 recusas, 1 nova tentativa. A mesma pergunta varia entre passadas
  (46 e 49 funcionaram numa e falharam na outra): a temperatura 0 não torna a saída do
  modelo idêntica quando o texto do esquema muda. É uma limitação a declarar.
- **Rodada cega INTERROMPIDA** na pergunta 77 por falta de créditos da API da Anthropic. A
  saída das 26 primeiras (51 a 76) se perdeu, porque o executor gravava só no fim. Do que
  saiu eu vi só "respondeu" e a base, nenhum resultado. O executor passou a gravar a cada
  pergunta e a aceitar `--retomar`. A rodada cega recomeça do zero depois que os créditos
  voltarem, e o artefato gravado registra o hash dos arquivos do sistema.
