# Plano de conclusão — TCC II (Bellestraiko)

> **Data-base: 2026-10-03.** Documento de trabalho gerado a partir da revisão
> de consistência (`docs/plano_contexto.md`, fases 0–5) e da geração do
> entregável em `.docx`.
>
> **Estado resumido:** de 6 pendências que o texto registrava, **4 estão
> fechadas**. Restam 2 decisões do orientador, 1 confirmação do autor e
> 2 itens opcionais que usam o espaço que sobrou no limite de páginas.
> **Não falta escrever texto.** O corpo tem 21 páginas de um limite de 25–30.

---

## Bloco 0 — O que já está pronto (não refazer)

| Entrega | Onde | Estado |
|---|---|---|
| Texto corrido do TCC II | `docs/tcc2_texto.md` (1.215 linhas) | completo |
| Entregável formatado | `docs/tcc2_final.docx` (49 págs) | gerado por script |
| Pipeline de geração | `docs/build_tcc_docx.py` + `finalize-fields.ps1` | automatizado |
| 5 Quadros numerados | campo `SEQ` do Word | automático |
| 6 Figuras do Anexo A | legenda no topo, fonte embaixo | automático |
| Sumário + Listas | 3 campos TOC | preenchidos pelo Word |
| 12 Referências ABNT | estilo `REFERÊNCIAS` + linha em branco | conforme |
| Correlação de código ↔ doc | 31/31 testes front, bateria exit 0 | verificado |

**Ao mexer em `tcc2_texto.md`, regere o `.docx`.** O documento não é editado
à mão — é build. Editar no Word e não propagar ao markdown faz o texto e o
entregável divergirem, que é o que a regra do projeto proíbe.

```powershell
$env:TCC1_REFERENCE_DOCX = 'C:\Users\Home\Downloads\TCC\TCC_Final.docx'
.\.venv\Scripts\python.exe docs\build_tcc_docx.py
powershell -ExecutionPolicy Bypass -File docs\finalize-fields.ps1
```

---

## Bloco 1 — Pendências que bloqueiam a entrega

Três itens. Os dois primeiros **dependem do Prof. Elvandi** — nenhum é
trabalho de escrita, é decisão de escopo.

### 1.1 Título acadêmico — ⚠️ bloqueia, precisa do orientador

**Estado:** aplicado um padrão, falta confirmar.

O título do TCC II foi mantido **igual ao TCC I** ("Plataforma Inteligente
para Análise de Dados de Esports: uma proposta para League of Legends com uso
de machine learning e interface em linguagem natural"). O raciocínio: TCC I e
TCC II são o mesmo trabalho, e trocar o título no meio sem aval cria uma
divergência entre os dois documentos que a banca pode estranhar.

Em vez disso o nome do produto foi registrado no **corpo**, na Seção 1.1
(página 10): *"A plataforma, batizada Bellestraiko, constitui a materialização
do sistema desenvolvido"*. Antes disso, Bellestraiko **não aparecia** no texto
entregue — só num bloco interno de pendências.

**Pergunta para o orientador:** o título deve citar Bellestraiko?

| Se a resposta for | O que fazer | Custo |
|---|---|---|
| Não, manter como está | nada | 0 |
| Sim, com Bellestraiko | `TITULO_PT` e `TITULO_EN` em `docs/build_tcc_docx.py` + regerar | 2 min |

---

### 1.2 Trabalhos Relacionados — ⚠️ bloqueia, precisa do orientador

**Estado:** mantido como nota dentro da Seção 2 (Referencial Teórico).

Existe uma assimetria real entre os documentos:

- **TCC I** tem `3 TRABALHOS RELACIONADOS` como **seção de primeiro nível**,
  aprovada.
- **Modelo institucional de 2026-09-28** (o que a coordenação mandou) **não
  inclui** essa seção.

O documento de pendências registra que, por acordo com o orientador, "a
estrutura de seções do corpo é livre, além de Introdução e Referencial
Teórico" — o que tira o caráter de bloqueio, mas não resolve a preferência.

**Pergunta para o orientador:** seção própria (como no TCC I) ou nota na
Seção 2 (como está)?

| Se a resposta for | Consequência | Custo |
|---|---|---|
| Nota na Seção 2 (atual) | nada | 0 |
| Seção de 1º nível | **a numeração de Material e Métodos em diante desloca** — e com ela sumário, listas e referências cruzadas. O pipeline absorve, mas tudo precisa ser regerado e conferido | ~15 min |

**Seção de primeiro nível exige também** promover o conteúdo atual da nota a
uma seção completa, com texto próprio — não só renumerar.

---

### 1.3 Título do Quadro 4 — ⚠️ bloqueia, precisa do autor

**Estado:** escrito, marcado como `CONFIRMAR com o autor` em
`docs/build_tcc_docx.py`, na lista `QUADROS`.

A tabela do Apêndice C (métricas completas, 4 cortes × 3 modelos) **não tinha
título** no markdown — só uma nota de método acima dela. Tabela sem legenda
viola a regra da instituição. O título foi escrito durante a conversão:

> **Quadro 4 — Métricas completas por corte temporal — comparação entre os três modelos**

**Decisão:** confirmar, trocar, ou deixar sem título e aceitar a não
conformidade. Custo: 2 min.

---

## Bloco 2 — Opcional, usa o espaço que sobrou

O corpo tem **21 páginas** num limite de **25–30**. Sobram 4 a 9. Nada abaixo
é obrigatório; os dois existem porque há espaço e porque ambos têm retorno
real, não porque o documento esteja incompleto.

### 2.1 Ampliar a amostra da NA1 — 🟢 maior retorno sobre esforço

**Por que:** a Seção 5.2 do próprio TCC declara a NA1 como o elo mais frágil
do achado de viés de lado. Está em **1.446 partidas** — cerca de um décimo da
BR1 (11.936) — e **não avançou** nas duas últimas rodadas de coleta, enquanto
EUW1 e KR quase dobraram.

É a **única** pendência da lista que adiciona *evidência* em vez de fechar
burocracia. E o achado é o pilar mais forte do trabalho: as quatro regiões com
amostra relevante pendem para o vermelho, e a NA1 é a única cujo volume não
sustenta a generalização.

**Custo:** roda em background, sem blocking. Chave de dev da Riot expira em
24h — se expirar, pedir **Personal API Key** no portal (sem expiração diária).
O banco está de pé com 33.713 partidas.

**Efeito no documento:** se entrar coleta nova, **os números do TCC
envelhecem**. Escolher **antes** de coletar:

| Opção | Consequência |
|---|---|
| Congelar em 33.713 (data de hoje) | nada a fazer; só escrever que a coleta continuou depois |
| Atualizar para o número novo | Atualizar Seção 4.3 (tabela regional), 4.2 (volume), 5.2 (limitação), e a entrada de diário. ~30 min de trabalho de consistência |

**Recomendação:** coletar, e atualizar. A NA1 é o único ponto onde o TCC admite
fragilidade, e é barato resolver.

### 2.2 Retreinar o modelo em 33.713 partidas — 🟡 retorno duvidoso

**Estado:** o modelo de produção foi treinado em **23.133** partidas. Os
hiperparâmetros foram tunados em 10k e **reaplicados** ao volume maior — não
houve `GridSearchCV` completo no volume final.

**A favor:** o próprio TCC registra que volume é o **único** lever que
funcionou (AUC 0,8214 → 0,8393 num ciclo). E há 10 mil partidas novas.

**Contra:** o diário registra que tuning por fase deu hiperparâmetros
**idênticos** aos de produção em 3 de 4 cortes — o ganho tende a ser
marginal. E reescrever a Seção 4.4 inteira + Apêndice C invalidaria trabalho
já conferido.

**Custo:** ~10 min de `tune_models` + `export_model` + bateria, **ou** ~2 h se
exigir reescrever Seção 4.4, Apêndice C e `handoff.md` com os números novos.

**Recomendação:** só se o orientador pedir tuning completo. É a mudança com
maior raio de-diff e menor retorno esperado.

---

## Bloco 3 — Fechamento

Executar quando os Blocos 1 e 2 estiverem resolvidos.

1. **Regerar** o entregável e conferir a contagem de páginas
   (`finalize-fields.ps1` já reporta).
2. **Revisão visual no Word** — duas coisas que o script não controla:
   - a **capa** (as posições verticais das linhas em branco não são idênticas
     às do TCC I; o pandoc não controla espaçamento vertical de capa);
   - a **legibilidade das 6 capturas** em 15 cm de largura.
3. **Testes** antes de fechar:
   ```powershell
   .venv\Scripts\python.exe tests\smoke_test.py        # exit 0
   .venv\Scripts\python.exe tests\validate_predictions.py  # exit 0
   cd frontend; npm run lint; npm run test; npm run build; cd ..
   ```
4. **Atualizar** `docs/handoff.md` e a lista de pendências do
   `diario_execucao.md` com o estado final.
5. **Commit** com mensagem no formato Conventional Commits em PT-BR.

---

## Ordem sugerida

```
1. Perguntar ao orientador (1.1 título + 1.2 Trabalhos Relacionados)
   └─ enquanto espera: decidir 1.3 (Quadro 4) e disparar 2.1 (NA1) em background
2. Aplicar as respostas; regerar
3. Se collect rodou: atualizar 4.3/4.2/5.2 + entrada de diário
4. Revisão visual no Word
5. Testes + commit
```

**Nada no Bloco 1 exige escrever texto novo.** São três decisões, das quais
duas são do orientador e uma é sua. O Bloco 2 é opcional por completo.

---

## Armadilhas conhecidas

- **Editar o `.docx` direto no Word** quebra a correspondência com o markdown.
  Sempre voltar por `tcc2_texto.md`.
- **Campos do Word nascem vazios.** Sem rodar `finalize-fields.ps1` o
  documento sai com sumário em branco e Quadros sem número.
- **A chave da Riot expira em 24h.** Erro 401/403 na coleta é isso, não é bug.
- **O `validate_predictions.py` roda ~26 s** e mostra `APROVADO COM
  RESSALVAS` com 1 `LIMITADO` e 3 `NEUTRO`. **Isso é o resultado esperado** —
  são as limitações que o TCC 5.2 declara, não regressão.
- **Resultado diferente no smoke test** (XGBoost abaixo de RandomForest) é
  normal: são 400 partidas sintéticas e diz nada sobre produção.