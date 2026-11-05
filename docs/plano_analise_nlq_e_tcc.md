# Planejamento de análise: (1) tudo o que foi feito na LLM e no SQL, (2) o que entra no TCC

Elaborado em 2026-11-05. Entrega do TCC: **16/11/2026** (11 dias). Corpo do texto: 29 de 30 páginas.
Este arquivo **planeja**; nada aqui foi aplicado ao texto do TCC. Os números vêm de artefatos; onde não há artefato, está dito.

---

## PARTE 1. Análise de tudo o que foi feito para melhorar a LLM e o SQL

### 1.1 Pergunta que a análise responde

> O que mudou no caminho pergunta → SQL → resultado, quanto cada mudança ajudou, o que ainda está errado, e que evidência temos para cada afirmação?

Hoje temos **três medidas diferentes**, que não podem ser somadas nem comparadas entre si:

| Conjunto | O que é | Quem julgou | Resultado | Vale como nota? |
|---|---|---|---|---|
| **Referência** (26) | Perguntas do `evaluate_nlq`, SQL esperada escrita pelo autor | Comparação automática do resultado | 23/26 no texto; **26/26 medido hoje** | Não é independente: as regras novas foram escritas sabendo das 3 falhas antigas |
| **Desenvolvimento** (50) | Perguntas livres 1–50, usadas para ajustar o esquema e o roteador | Ninguém (só "respondeu / recusou / errou") | 48/50 responderam, 8 recusas, 2 erros | **Não**: foi usado para ajustar o sistema; além disso nunca teve veredito humano |
| **Cego** (50) | Perguntas 51–100, rodadas **uma vez**, com sistema congelado (hashes gravados) | Conferência contra o banco, com consulta independente por pergunta | **31/50 certas (62%)**; 36/50 com parcial valendo meio ponto | **Sim**, com ressalvas (1.5) |

### 1.2 Inventário do que mudou (por camada)

Estado: o commit `66bfe7a` tem o validador e a nova tentativa; **todo o resto está sem commit**.

| # | Camada | O que mudou | Onde | Motivo | Evidência hoje | Commit |
|---|---|---|---|---|---|---|
| 1 | Validador | Reescrito como falha fechada: analisador de tokens para achar as tabelas de verdade (inclusive junção por vírgula), rejeita aspas, comentários, `$`, `\`, `E''`, `U&`; palavras proibidas ampliadas (`into`, `nextval`, `setval`, `for update`); lista de funções perigosas (`pg_read_file`, `dblink*`, `query_to_xml`, `set_config`, `pg_sleep*`...); `EXTRACT/TRIM/SUBSTRING` com `FROM` tratados | `src/nlq/sql_guard.py` | Auditoria achou buracos reais (junção por vírgula, `query_to_xml`, `pg_read_file`, `E''`) | `tests/test_validate_sql.py`: 24 consultas legítimas passam, 36 maliciosas bloqueiam, as 52 do benchmark passam | Parcial (`66bfe7a`); funções de base **sem commit** |
| 2 | Guarda de base | `SOLO_TABLES`, `PRO_TABLES`, `validate_base`, `BaseMixError`: uma SQL não pode misturar as duas bases | `sql_guard.py`, `nl_to_sql.py` | As duas bases têm convenções diferentes; misturar dava resposta sem sentido | `tests/test_ask_base.py` | Não |
| 3 | Nova tentativa | **Uma** nova geração, passando o erro do banco ao modelo (ou a mistura de bases); `QueryCanceled` não é refeito; devolve `tentativas` | `ask_base` | 4 de 50 perguntas livres falhavam por erro de SQL | `tests/test_ask_retry.py`; no cego, 2 resultados usaram a 2ª tentativa | Parcial |
| 4 | Esquema dado ao modelo | `game_creation` é TIMESTAMPTZ; bans sem data; regras de desambiguação solo × competitivo; amostra mínima (≥20 solo, ≥10 competitivo) em ranking de taxa; `NULLS LAST`; "o X de cada Y" com `ROW_NUMBER`; lista do que **não existe** (pentakill, "primeiro X", ouro/CS/dano/visão/banimento no competitivo) com exemplo de recusa | `src/nlq/schema_context.py` | Falhas do desenvolvimento e colunas reais do banco | Benchmark 26/26; dev: pentakill (28) recusa, ranking com nulos (35) corrigido | Não |
| 5 | Roteador | Classifica SOLO / COMPETITIVO / AMBOS: regras por pistas do esquema, **herança** da base da pergunta anterior, **Haiku** só no resíduo (`max_tokens=16`, só a 1ª linha da resposta); saída inválida ou exceção → AMBOS | `src/nlq/route.py` | A maior parte dos erros do desenvolvimento era escolher a base errada | `tests/test_route.py`, `tests/test_ask_route.py`; no cego: 40 perguntas para uma base, 9 para as duas | Não |
| 6 | Resposta por base | `ask` roda uma ou duas bases e devolve `resultados` por base; se todas falham, levanta a última exceção | `nl_to_sql.py`, `src/api/main.py` | Pergunta ambígua deve mostrar as duas respostas, não escolher no escuro | `tests/test_api_ask.py` | Não |
| 7 | Tela | Painéis lado a lado em AMBOS, selo de base, explicação sob demanda, histórico com uma entrada por base | `frontend/src/pages/Nlq.tsx`, `lib/api.ts`, `lib/format.ts` | Consequência do item 6 | `Nlq.test.tsx` (6 testes) | Não |
| 8 | Medição | Executor do conjunto (`avaliar_conjunto`): grava a cada pergunta, hashes dos 4 arquivos do sistema, para limpo em erro externo, `--retomar` | `src/nlq/avaliar_conjunto.py` | Rodada cega interrompida por falta de créditos perdeu 26 respostas | Teste com falsos (parou na 2, retomou 2 e 3) | Não |
| 9 | Dados | Banco voltou a 41.063 partidas (backup + remoção das coletas posteriores a 3/11 18:00, em transação) | PostgreSQL | O banco tinha 42.160 e o TCC cita 41.063 | Contagem conferida antes do commit | n/a |

### 1.3 O que sabemos e o que **não** sabemos

**Sabemos (com artefato):**
- O validador bloqueia 36 de 36 ataques testados e aceita as 52 consultas do benchmark e as 24 legítimas.
- No cego, **0 resultados com erro de banco**. O executor contou 9 resultados de recusa: 7 perguntas com recusa certa (55, 77, 83, 88, 89, 91, 95), a recusa do lado competitivo da 59 (a pergunta saiu certa porque o lado solo respondeu) e 1 recusa errada (75). O sistema recusa pouco e, quando recusa, quase sempre acerta.
- O pior tipo de falha é a **resposta errada com cara de certa**: 74, 82, 94, 72, 80, 62 e 76 devolvem um número ou lista plausível e errado (**7 de 50, 14%**). Falhas visíveis (erro 86, recusa errada 75) são só 2.
- O sistema erra por **padrões**, não ao acaso (1.4).

**Não sabemos (ainda):**
1. Quanto de cada melhoria vem de qual mudança (nunca rodamos o sistema antigo sobre o cego).
2. A acurácia do roteador sozinho (a base escolhida estava certa?).
3. Quanto a mesma pergunta varia entre passadas (só temos 2 casos observados no desenvolvimento).
4. Se o usuário do banco tem permissão de escrita. **A conexão não é somente leitura**: o código só define `statement_timeout`. A defesa depende só do validador.
5. Custo e latência por pergunta (nada foi gravado).
6. Se o desenvolvimento, com 20 respostas incertas, estava certo (nunca houve veredito humano).

### 1.4 Falhas do cego agrupadas (já feito, a formalizar)

| Família | Perguntas | Tipo | Consertável de forma geral? |
|---|---|---|---|
| Sem filtro de amostra mínima no competitivo | 71, 73, 93 (e 72) | Silenciosa | Sim: regra no esquema, mas a regra já existe só para taxa de vitória |
| Lista cortada pelo `LIMIT 100` automático | 58, 65 | Silenciosa | Sim: avisar que cortou, ou subir o limite |
| Ano e "principais ligas" ignorados | 76, 94, 100 | Silenciosa | Em parte: "principais ligas" precisa de uma definição |
| Sequência (run-length) montada errada | 74 | Silenciosa | Difícil: SQL de janela |
| Recusa errada (coluna existia) | 75 | Visível | Sim: o esquema precisa dizer que `game_date` existe |
| Agregação por linha de jogador em vez de equipe ou jogo | 72, 80 | Silenciosa | Sim: regra "equipe = `pro_games`, uma linha por lado" |
| Tabela de 2 linhas por jogo (contagem de jogos) | 82, 86, 90 | Silenciosa / erro / parcial | Sim: regra e exemplo |
| Rótulo falso (escolhas chamadas de `bans`) | 94 | Silenciosa, **viola honestidade** | Sim: regra "competitivo não tem bans" já existe e **não foi obedecida** |
| Pergunta ambígua | 52, 62, 81, 98 | Parcial | Em parte |

### 1.5 Limites da própria medição (a declarar no TCC)

- **O julgamento do cego foi meu** (a pedido do usuário, com consulta independente no banco). Não houve segundo avaliador humano. O usuário pode contestar qualquer veredito; há 50 justificativas em `reports/nlq_cego_vereditos.json`.
- Vi o **texto** das 50 perguntas cegas antes de congelar o sistema. O exemplo de recusa sobre ouro total de equipe que acrescentei ao esquema toca em tema que o cego também sonda (disclosure no plano de roteamento).
- 50 perguntas dão margem ampla: 31/50 tem intervalo de 95% de Wilson de cerca de **48% a 74%**. Isso precisa aparecer junto do número.
- Temperatura 0 **não** garante a mesma saída quando o texto do esquema muda (46 e 49 do desenvolvimento).
- O benchmark de 26 usa o mesmo caminho do produto? **A confirmar**: a Fase 5 previa `evaluate_nlq --produto` (usar `ask`) e isso não foi feito.

### 1.6 Análises a executar (em ordem de valor para o TCC)

| ID | Análise | Método | Artefato | Custo | Prioridade |
|---|---|---|---|---|---|
| A1 | **Quanto o roteamento ajudou** | Rodar o código de antes (commit `3b7e353`, worktree) sobre as mesmas 50 perguntas cegas, mesma conferência; comparar por pergunta | `reports/nlq_cego_antigo.json` + vereditos | Poucos centavos; conferência manual de ~50 | Alta (é o argumento central da seção) |
| A2 | **Acurácia do roteador** | Rotular a base certa de cada pergunta (dev + cego = 100) por pista, matriz de confusão e quebra por origem (regras / herança / modelo / padrão) | `reports/nlq_roteador_rotulos.json` | Rotulagem de 100, sem API | Alta |
| A3 | **Estabilidade** | Repetir o cego 3 vezes sem alterar nada; contar perguntas cujo veredito muda | `reports/nlq_cego_repeticoes.json` | ~10 min por passada; conferência só das que mudarem | Alta (sustenta a limitação) |
| A4 | **Falhas silenciosas × visíveis** | Formalizar a tabela 1.4 com contagem (já está nos vereditos) | Quadro no Apêndice B | Sem custo | Alta |
| A5 | **Segurança em profundidade** | (a) confirmar privilégios do usuário do banco; (b) registrar se a transação é somente leitura; (c) listar o que o validador bloqueia, por categoria | Texto + teste novo | Baixo; (b) exige 1 linha de código | Média-alta; é código, pedir autorização |
| A6 | **Revisão humana de amostra** | O usuário confere ~10 vereditos (os 9 erros + 1 certa) para poder dizer que houve revisão humana | Marca na folha | 20 min do usuário | Média-alta |
| A7 | **Desenvolvimento com veredito** | Julgar as 20 respostas incertas do dev (folha já gerada), para saber se o dev mede algo | `docs/revisao_nlq_incertas.md` | Tempo do usuário | Baixa (não vai ao texto como nota) |
| A8 | **Caminho do produto no benchmark** | `evaluate_nlq --produto` usando `ask` | `reports/nlq_benchmark_produto.json` | Chamada de API (26) | Média |
| A9 | **Custo e latência** | Registrar tempo e tokens por pergunta em uma passada | Coluna nova no artefato | Baixo | Baixa |
| A10 | **Portão final** | `pytest`, `vitest`, `lint`, `build`, `verifica_tcc`, `confere_docx` | Saída dos comandos | Minutos | Obrigatória antes de qualquer commit de fechamento |

**Regra de ouro dos extras:** nada disso ajusta o sistema com base no cego. A1 e A3 só **medem**.
Se quisermos **corrigir** os padrões da tabela 1.4, a correção vale como novo desenvolvimento e a medida do cego (v1) fica congelada; para provar a correção precisaríamos de um terceiro conjunto (v2). Não recomendo gastar o prazo nisso.

---

## PARTE 2. Análise do que adicionar (e mudar) no TCC

### 2.1 Princípios

1. **Três medidas, três rótulos.** Referência (26), desenvolvimento (50, sem nota) e cego (50, 31/50). O texto nunca mistura as três.
2. **O número que se defende é o do cego**, com intervalo, tamanho da amostra, quem julgou e como.
3. **Dizer onde o sistema falha** é parte do resultado; o argumento do trabalho é a separação entre dado medido e inferência, e o NLQ tem de seguir essa linha.
4. **Orçamento de páginas:** o corpo está em 29/30. O que entra no corpo precisa sair ou ir para o apêndice.

### 2.2 O que o texto afirma hoje e fica desatualizado

| Onde | Afirmação atual | Problema |
|---|---|---|
| Resumo (l. 51–52) e *Abstract* (l. 76) | "88% de acurácia de execução em um benchmark de 26 perguntas" | Verdadeiro, mas é a medida **fraca**; o leitor só vê o número favorável |
| 1.4 g (l. 194) | "propor uma interface em linguagem natural" | Sem mudança, mas o resultado (5.6) precisa responder a esta frase |
| 3.6 (l. 398) | "26 perguntas fixas e resposta esperada conferida contra o banco" | Falta o conjunto cego |
| 4.7 (l. 506–514) | Fluxo text-to-SQL sem roteamento, sem guarda de base, sem nova tentativa | Descreve o sistema antigo |
| 5.6 (l. 744–765) | 23/26 (88%), Quadro 6 por tipo, três falhas "do mesmo tipo" | O sistema hoje dá 26/26; as 3 falhas foram corrigidas **sabendo-se delas** |
| Conclusão (l. 837–838) | "88% ... 26 perguntas" | Idem Resumo |
| 6.1 (l. 859–898) | **Não há nenhuma limitação do NLQ** | Lacuna principal: o cego revela falhas silenciosas |
| 6.2 (l. 902) | "cinco caminhos" | Passam a ser seis, com trabalhos de NLQ |
| Apêndice B (l. 1091–1145) | Tabela de execuções 23/26 e 26 perguntas | Falta a execução de 5/11 (26/26), o cego e a explicação de não ser independente |
| Apêndice F (l. 1355) | Quadro de limitações sem NLQ | Falta a linha do NLQ |
| Apêndice I (l. 1460) | Linha g: "23 de 26 (88%), Quadro 6" | Atualizar |
| `fig_nlq.png` (Figura 5) | Captura da tela antiga | A tela agora tem painéis por base; refazer a captura com Playwright |
| Pendências finais (l. 1545 em diante) | Dizem "nenhuma pendência" e "88% confirmado" | Deixam de ser verdade |

### 2.3 O que adicionar, seção por seção

**Resumo e *Abstract*** (duas frases, mesma estrutura):
> "... A interface de consulta em linguagem natural acertou 23 das 26 perguntas de referência (88%) e, em um conjunto cego de 50 perguntas conferidas contra o banco, 31 (62%), com falhas concentradas em agregações de equipe e filtros de amostra."
Decisão D7 (abaixo).

**4.7** (+3 frases, sem aumentar o parágrafo): o fluxo agora (i) classifica a pergunta em solo, competitivo ou ambas, por regras sobre o esquema e um modelo pequeno só no que sobra, (ii) impede que uma consulta misture as duas bases, (iii) refaz a consulta uma vez com a mensagem de erro do banco. O resto vai para o Apêndice B.

**5.6** (reescrever, mesmo tamanho):
1. Parágrafo da **medida de referência** (26, 26/26 hoje, 23/26 antes) com a frase "não é independente: as regras do esquema foram escritas depois de ver as três falhas".
2. Parágrafo do **cego** (50; protocolo em uma frase; resultado C/RC/P/E/RE; intervalo 48%–74%).
3. **Quadro novo:** veredito por família de falha (tabela 1.4 reduzida a 5 linhas). O Quadro 6 atual (por tipo de pergunta) **vai para o Apêndice B**, e o novo ocupa o lugar dele no corpo.
4. Frase-chave: "7 das 50 respostas foram erradas e plausíveis; só 2 falharam de forma visível."
5. Figura 5 refeita com a tela nova.

**6.1** (novo parágrafo "Validade da consulta em linguagem natural", ~8 linhas): amostra de 50 e intervalo; um avaliador só; sem segunda leitura; saída que varia entre passadas mesmo com temperatura 0 (A3); falhas silenciosas (7/50); ambiguidade solo × competitivo; teto de 100 linhas; defesa só por validação (A5); conjunto de referência não independente.

**6.2** (+1 caminho): amostra mínima e verificação semântica depois da execução (conferir o valor devolvido contra uma consulta de verificação), avaliação sobre mais de um banco (Zhong; Yu; Klein, 2020, já citado em 4.7), conjunto cego maior com dois avaliadores.

**Apêndice B** (cresce; apêndice não conta no limite):
- Linha nova na tabela de execuções: 5 de novembro, 41.063, 26/26, "depois das regras de esquema, **não independente**".
- Seção "Conjunto cego": protocolo (perguntas de fora do desenvolvimento, sistema congelado com hashes, uma passada, julgamento contra o banco), quadro das 50 (n, base, veredito, motivo em uma linha), quadro das falhas, quadro de roteamento (A2), quadro de repetições (A3), comparação com o sistema antigo (A1).
- Comandos: `avaliar_conjunto` e artefatos.
- O Quadro 6 por tipo, vindo do corpo.

**Apêndice F:** linha "Consulta em linguagem natural" com evidência (31/50; 7 silenciosas) e tratamento (limitações declaradas; sem ajuste pós-medida).

**Apêndice I:** linha g atualizada.

**Referências:** nada obrigatório. Opcional, só se for citar: BIRD / Spider para avaliação de text-to-SQL; **conferir contra o texto do artigo** antes (regra do projeto, três atribuições erradas já apareceram).

### 2.4 Documentos de apoio e verificações

| Item | Ação |
|---|---|
| `verifica_tcc.py`, checagem 19 | Hoje **vermelha** (texto 23/26, artefato 26/26). Ensinar a checagem a ler: benchmark (26/26 e a ressalva) **e** `reports/nlq_cego_vereditos.json` (contagens do texto = contagens do JSON) |
| `confere_docx.py` | Rodar após o build; conferir páginas do corpo (≤30) e o Quadro/Figura renumerados |
| Guias, site de estudo, defesa (`bellestraiko_defesa.pptx`) | Atualizar números e a resposta pronta "por que 62% e não 88%?" |
| `docs/comandos.md`, `scripts.md`, `handoff.md`, `README.md` | Comandos de `avaliar_conjunto`, roteador, guarda de base |
| `docs/perguntas_orientador.md` | Acrescentar D7 e a pergunta de autoria das perguntas cegas |
| Memória do projeto | Já registra o cego (31/50) |

### 2.5 Orçamento de páginas

Corpo: 29/30. Mudanças no corpo: 4.7 (+3 frases), 5.6 (reescrita no mesmo espaço, Quadro 6 sai, quadro novo entra), 6.1 (+1 parágrafo de ~8 linhas), 6.2 (+1 frase), Resumo (+1 frase). Saldo esperado: +10 a +14 linhas, que **consome a folga de 1 página**. Se estourar: encurtar 6.1 e passar a lista de limitações do NLQ para o Apêndice F, deixando no corpo só as duas mais graves.

### 2.6 Cronograma até 16/11

| Dia | Entrega |
|---|---|
| 5/11 (qui) | Decisões D7–D11; commit; A4, A2 (rotulagem) |
| 6/11 (sex) | A1 (sistema antigo no cego) e A3 (3 repetições); A6 (usuário confere amostra) |
| 7–8/11 (fim de semana) | Escrever 4.7, 5.6, 6.1, 6.2, Resumo, Apêndice B/F/I; refazer Figura 5; `verifica_tcc` |
| 9/11 (seg) | Build do docx, `finalize-fields`, `confere_docx`; conferir páginas |
| 10–11/11 | Atualizar guias, site de estudo e defesa |
| 12–13/11 | Releitura completa do PDF; correções; A10 (portão) |
| 14/11 | **Congelar o texto** |
| 15/11 | Folga e ensaio da demonstração |
| 16/11 | Entrega |

### 2.7 Riscos

| Risco | Probabilidade | Resposta |
|---|---|---|
| O orientador estranhar 62% ao lado de 88% | Média | Explicar no texto por que as duas existem; é a parte mais defensável do trabalho |
| Estourar 30 páginas | Média | Plano de corte em 2.5 |
| Banca questionar a avaliação feita pela própria IA que escreveu o sistema | Média-alta | A6 (revisão humana de amostra) e veredito com consulta SQL reproduzível; declarar a limitação |
| Banco de dados mudar (nova coleta) e invalidar números | Baixa | Não coletar até a entrega; o artefato do cego grava data e hashes |
| Alguém rodar o executor de novo e sobrescrever o cego | Baixa | Não versionar com o mesmo nome; copiar o artefato antes de A3 |

---

## Decisões abertas (suas)

| ID | Decisão | Recomendação |
|---|---|---|
| **D7** | Como citar o NLQ no Resumo e na Conclusão | Os dois números, referência (88%) e cego (62%), com o cego explicado em meia linha |
| **D8** | Quem escreveu as 50 perguntas cegas (precisa estar no método) e se você confere uma amostra dos vereditos (A6) | Descrever a autoria como ela foi; conferir os 9 erros e 1 certa |
| **D9** | Rodar A1 (sistema antigo no cego) e A3 (3 repetições) | Sim: só medem, custam pouco e dão o argumento central de 5.6 |
| **D10** | Corrigir os padrões de falha antes da entrega | Não ajustar prompt; **única exceção** é a transação somente leitura (A5), que é segurança e não muda acurácia |
| **D11** | Autorização para commitar (dois commits: sistema de consulta com testes; frontend) | Fazer **antes** de A1 e A3, para o artefato apontar o commit medido |
| **D12** | Levar ao orientador: vale mostrar o cego e o 62%? | Sim, junto com 14, 30, 43 e 44 |

Já decidido antes: D1–D6 do plano de roteamento.
