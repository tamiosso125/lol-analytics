# Handoff — Bellestraiko (TCC II)

> Renomeado 2× em 2026-07-03: "LoL Analytics" colidia com lolalytics.com,
> "Hextech Lab" com um canal do YouTube. Nome atual: Bellestraiko.

Documento para quem retomar o projeto "a frio" (você mesmo depois de um tempo,
ou outra pessoa) — resume o que existe, por que existe, o que falta e onde
olhar para mais detalhes. Não repete o histórico passo a passo (isso está em
`docs/diario_execucao.md`) nem a referência de cada script (`docs/scripts.md`)
— este documento é o mapa de alto nível que aponta para os dois.

## O que é o projeto

TCC II (CS, Unisinos): plataforma de análise de esports de League of Legends.
Coleta partidas ranqueadas (fila solo, queue 420) de Challenger/Grandmaster do
Brasil via Riot API, guarda em PostgreSQL, treina modelos de predição de
vitória "em jogo" (estado da partida em um corte de tempo — não pré-jogo por
composição), expõe tudo via API FastAPI e um front end React, e tem uma
interface de perguntas em linguagem natural (text-to-SQL) sobre os dados.

**Estado atual**: as 6 etapas do roadmap original estão concluídas com dados
reais. Dataset: **10.402 partidas**, 10.537 jogadores, 11 patches (16.10 a
16.13), 96.696 banimentos. Front end React é a interface principal; o
Streamlit (`src/dashboard/app.py`) segue existindo como alternativa mais
simples (consulta o banco direto, não passa pela API).

## Arquitetura (visão rápida)

```
Riot API → coletor (rate-limited) → raw_matches/raw_timelines (JSONB)
                                          │ ETL (src/etl/load_matches.py)
                                          ▼
                 matches / teams / participants / players / bans (normalizadas)
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              ▼                           ▼                           ▼
   features por fase (10/15/20/25   modelos RF/XGB/MLP          API FastAPI
   min, build_features.py)          por fase (export_model.py)  (src/api/main.py)
                                                                       │
                                                          ┌────────────┴────────────┐
                                                          ▼                         ▼
                                                  frontend/ (React,           Streamlit
                                                  interface principal)        (alternativa)
```

Decisão central do escopo de predição: **estado em jogo, não pré-jogo por
composição** (metodologia de Hodge et al., 2021) — features são diffs
azul−vermelho (ouro, XP, abates, torres, dragões) extraídos das timelines em
4 cortes de tempo, nunca totais finais da partida (isso seria vazamento de
dados). Ver o aviso no topo de `src/features/build_features.py`.

Um segundo modelo, **não-ML**, existe para composições: `/compose` (usado
pela página "Montar Partida") é uma heurística de win rates históricos de
matchup por lane e sinergia de dupla — deliberadamente separado do modelo ML
e sem o viés de lado embutido. A UI é explícita sobre essa distinção porque a
banca tende a perguntar sobre ela.

## Onde estão as coisas

- **Schema**: `db/schema.sql` — `players`, `raw_matches`/`raw_timelines`
  (JSONB bruto para reprocessamento), `matches`, `teams`, `participants`,
  `bans`.
- **Coleta**: `src/collect/` (`seed_players.py`, `collect_matches.py`,
  `backfill_names.py`) — rate limit de 100 req/2min (chave de
  desenvolvedor), expira a cada 24h.
- **ETL**: `src/etl/load_matches.py` — popula as tabelas normalizadas a
  partir do JSON bruto; idempotente (pode reprocessar).
- **Features**: `src/features/build_features.py` — `CUTOFFS = [10, 15, 20,
  25]`; gera `data/features_phases.csv` (todas as fases) e
  `data/features.csv` (só o corte de 15 min, compat. com scripts antigos).
- **Modelos**: `src/models/` — `train_baseline.py` (RF/XGB/MLP sem tuning),
  `tune_models.py` (GridSearchCV + calibração), `export_model.py` (treina e
  exporta um modelo POR FASE para produção, mais importância SHAP),
  `explain_shap.py` (gráficos para o capítulo de explicabilidade).
- **API**: `src/api/main.py` — FastAPI, todos os endpoints de
  estatísticas/predição/composição/NLQ. Ver `docs/scripts.md` para a lista
  completa de rotas.
- **NLQ**: `src/nlq/` — `nl_to_sql.py` (geração + validação de segurança +
  execução), `schema_context.py` (prompt de sistema com o schema e as
  regras), `evaluate_nlq.py` (benchmark de 22 perguntas, execution accuracy).
- **Front end**: `frontend/` — Vite + React 19 + TypeScript + Tailwind v4 +
  Recharts + TanStack Query + React Router. Consome só a API (nunca o
  banco). Páginas: Início, Dashboard, Campeões (+ detalhe), Partidas (+
  análise com mapa de calor), Consulta NL, Predição, Montar Partida,
  Explicabilidade.
- **Streamlit**: `src/dashboard/app.py` — alternativa mais simples, consulta
  o banco direto. Único script do projeto que não roda via `python -m`
  (insere `sys.path` manualmente no topo).
- **Documentação**: `docs/diario_execucao.md` (histórico cronológico de
  decisões e resultados — a fonte para escrever os capítulos do TCC),
  `docs/scripts.md` (referência de cada script/endpoint/página).
- **Memória do assistente**: se você está retomando isso com o Claude Code,
  o histórico de contexto (preferências, feedback, estado do projeto) está
  em `C:\Users\Home\.claude\projects\...\memory\` — não precisa
  reconstruir isso na mão, ele lê sozinho.

## Números que importam (para o texto do TCC)

Modelos tunados no dataset completo (10.295 partidas com features aos 15
min; ver `reports/tune_models_10k.log` e a entrada de 2026-07-03 no diário):

| Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---|---|---|---|---|
| MLP | 0,7522 | 0,7268 | 0,6919 | 0,7089 | **0,8325** |
| XGBoost | 0,7501 | 0,7212 | 0,6959 | 0,7083 | 0,8319 |
| RandomForest | 0,7507 | 0,7186 | 0,7039 | 0,7111 | 0,8305 |

XGBoost tunado usado em produção (por fase): `n_estimators=500,
learning_rate=0.01, max_depth=3`.

Interface NL: **20/22 = 91% execution accuracy** (não 95% — esse número
antigo ficou defasado quando o prompt cresceu; ver "Limitações conhecidas"
abaixo). Re-medir com `python -m src.nlq.evaluate_nlq` sempre que
`schema_context.py` mudar.

Achado de tese (inversão do consenso da literatura): a literatura geral
aponta leve vantagem do lado azul no solo queue (~50,6–53%), mas neste
recorte (Challenger/GM BR) o **lado vermelho vence 56,3%** das partidas —
estável em todos os 11 patches. Hipótese registrada no diário: counter-pick
garantido pesa mais no elo onde todos punem draft, somado ao acesso ao pit
do dragão.

Importância SHAP por fase: `tower_diff` sai de quase irrelevante aos 10-15
min (as placas de torre só caem aos 14 min) para um fator relevante no late
game — a razão exata está no gráfico de evolução da página Explicabilidade,
calculada dinamicamente do JSON (não cite um multiplicador fixo no texto do
TCC, ele muda a cada retreino).

## Como rodar

Ver `README.md` para o passo a passo completo. Resumo:

```bash
# backend
uvicorn src.api.main:app --reload          # API em :8000

# frontend
cd frontend && npm install && npm run dev  # Vite em :5173 (precisa da API rodando)

# alternativa mais simples
streamlit run src/dashboard/app.py
```

Pré-requisitos: PostgreSQL com o schema aplicado (`python -m src.db`),
`.env` preenchido (`RIOT_API_KEY` — expira em 24h — `DATABASE_URL`,
`ANTHROPIC_API_KEY` para o NLQ).

## Limitações conhecidas (documentar no texto, não "resolver às pressas")

- **Amostras pequenas em matchups/sinergias específicos**: perguntas do
  tipo "campeão X + campeão Y" no NLQ ou no `/compose` podem ter n < 20 e
  o resultado varia muito por acaso. O `/compose` já corta em ≥10
  (matchup) / ≥20 (sinergia) jogos e sinaliza a fonte; o NLQ (desde a
  revisão de 2026-07-03) avisa explicitamente quando a amostra é pequena e
  separa "leitura de jogo" (conhecimento do LLM sobre o jogo, rotulado
  como tal) da leitura estatística. Correção formal (shrinkage/intervalo
  de confiança) é um incremento futuro, não implementado.
- **NLQ benchmark tem 2 falhas conhecidas e aceitas**: uma pergunta gera
  uma coluna extra de contagem quando a pergunta menciona um limiar de
  jogos; outra responde com o nome do time ("Vermelho") em vez do
  team_id numérico quando a própria pergunta usa esse nome — ambas
  corretas para um humano, mas o benchmark faz exact-match contra o SQL
  de referência. Deliberadamente não "consertadas" para não fazer
  overfitting do prompt ao benchmark.
- **Cobertura por patch é desigual**: o patch 16.13 concentra ~50% do
  dataset; métricas de meta (win/ban rate por campeão) refletem sobretudo
  essa versão. Isso está exposto no Dashboard (gráfico de cobertura), não
  escondido.
- **Team builder (Montar Partida) não modela jogadores nem itens/nível
  explícitos** — só campeões e um estado agregado opcional (ouro/XP/
  abates/objetivos por diff, combinado ao modelo ML em log-odds). Ver
  pendências abaixo.
- **Chave de API de desenvolvedor** expira a cada 24h e tem rate limit de
  100 req/2min — coleta adicional precisa ser rodada em sessões, ou trocar
  por uma Personal API Key (sem expiração diária) se for coletar mais.

## Pendências / próximos passos

Em ordem aproximada de valor para o TCC:

1. **Escrever os capítulos do TCC II** usando `docs/diario_execucao.md`
   como fonte primária — é onde cada decisão, número e achado já está
   registrado com contexto e data. Não é preciso reconstruir nada, é
   compilar.
2. **Team builder — incrementos da visão original**: jogadores na análise
   de composição (hoje só campeões) e champion select competitivo. Ver
   `[[project-team-builder]]` na memória do assistente para o contexto
   completo do que já foi decidido.
3. **Correção estatística de amostra pequena** (shrinkage/IC) para
   sinergias/matchups específicos, tanto no `/compose` quanto nas respostas
   do NLQ.
4. **Meta de predição em tempo real** (jogo ao vivo) — é uma direção
   futura explicitamente adiada; não foi bloqueada arquiteturalmente (o
   `/predict` já aceita qualquer minuto/estado), mas nada foi feito ainda.
5. Coleta adicional se quiser diversificar a cobertura de patches (hoje
   desbalanceada para o 16.13).

## Regras/convenções que valem a pena lembrar

- Todo script roda via `python -m src.xxx` (exceto o Streamlit, que precisa
  do `sys.path` manual — comentado no topo do arquivo).
- Nunca usar estado pós-corte ou totais finais como feature de predição em
  jogo — é vazamento de dados. O schema do NLQ também avisa o LLM sobre
  isso explicitamente (perguntas tipo "quanto de ouro tinha aos 21 min" não
  são respondíveis pelo schema relacional, só pela timeline bruta).
- Ícones de campeão vêm do CDN CommunityDragon por `champion_id` (evita
  divergência de nome entre o match-v5 da Riot e o Data Dragon).
- Ao mexer em schema ou features, atualizar o README (regra do projeto).
- Ao mexer no `schema_context.py` do NLQ, **rodar `evaluate_nlq.py` de
  novo** — já regrediu uma vez silenciosamente (95% → 77%) sem essa
  disciplina.
- Testes (`tests/smoke_test.py`) rodam em diretório temporário desde a
  revisão de 2026-07-03 — não devem mais tocar em `data/features.csv` real.
