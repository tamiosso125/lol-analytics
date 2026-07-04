# Hextech Lab — Plataforma de Análise de Dados de Esports (TCC)

> Renomeado de "LoL Analytics" em 2026-07-03 — o nome colidia com o site
> já existente lolalytics.com. O diretório do repositório continua se
> chamando `lol-analytics` (não renomeado, para não quebrar caminhos).

Scaffold inicial da plataforma proposta no TCC 1: coleta via Riot Games API,
armazenamento em PostgreSQL, ETL, features e baseline de modelos preditivos.

## Arquitetura

```
Riot API ──> coletor (rate-limited) ──> raw_matches/raw_timelines (JSONB)
                                              │ ETL
                                              ▼
                       matches / teams / participants / players / bans
                                              │
                          ┌───────────────────┼──────────────────┐
                          ▼                   ▼                  ▼
                    EDA (4.5)        features + modelos     dashboards +
                                     RF/XGB/MLP (4.6)       interface NL (4.7)
                                                            [próximas etapas]
```

## Setup

1. PostgreSQL rodando e banco criado: `createdb lol_analytics`
2. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. `cp .env.example .env` e preencha `RIOT_API_KEY`
   (chave de dev expira a cada 24h — renove em developer.riotgames.com).
   Para a interface em linguagem natural, adicione também `ANTHROPIC_API_KEY`.

## Ordem de execução

Antes de tudo, valide o ambiente sem banco nem API:

```bash
python tests/smoke_test.py     # pipeline features -> modelos com dados sintéticos
```

Depois, com PostgreSQL e chave configurados:

```bash
python -m src.db                              # 1. aplica o schema
python -m src.collect.seed_players            # 2. semeia jogadores (Challenger/GM)
python -m src.collect.collect_matches --players 50 --matches-per-player 20
                                              # 3. coleta partidas + timelines
python notebooks/01_eda.py                    # 4. análise exploratória
python -m src.features.build_features         # 5. features por fase (10/15/20/25 min)
python -m src.models.train_baseline           # 6. compara RF / XGBoost / MLP
python -m src.models.tune_models              # 7. tuning + curva de calibração
python -m src.nlq.nl_to_sql "qual campeão tem maior win rate?"
                                              # 8. consulta em linguagem natural
python -m src.nlq.evaluate_nlq                # 9. valida a interface NL (banca)
uvicorn src.api.main:app --reload             # 10. API para os dashboards
streamlit run src/dashboard/app.py            # 11. dashboards interativos
python -m src.models.explain_shap             # 12. explicabilidade (SHAP)
python -m src.models.export_model             # 13. exporta os modelos p/ a API (/predict)
```

## Front end (React)

Interface principal da plataforma em `frontend/` (Vite + React + TypeScript,
Tailwind CSS v4, Recharts, TanStack Query). Páginas: início (busca de
campeão, rankings top-5 e insights com o "porquê"), dashboard analítico
em seções narrativas (ouro × vitória, objetivos, viés de lado, durações,
cobertura por patch), campeões (tabela win/pick/ban rate estilo op.gg,
com detalhe e matchups por campeão), partidas (feed + análise completa
com curva de probabilidade minuto a minuto, mapa de calor sobre o
minimapa e objetivos por minuto), consulta em linguagem natural (com
explicação e chat de acompanhamento), predição de vitória por fase do
jogo (10/15/20/25 min), montar partida (team builder 5v5 com matchups,
sinergias e estado de jogo opcional) e explicabilidade (SHAP por fase +
evolução da importância) — tudo consumindo a API FastAPI (o Streamlit
segue disponível como alternativa). Ícones de campeão via CDN
CommunityDragon.

Obs.: a tabela `bans` é preenchida pelo ETL; se o banco foi populado antes
dela existir, rode `python -m src.etl.load_matches` uma vez (backfill a
partir dos payloads brutos, idempotente).

Obs. 2: a tabela `item_events` (compras/vendas de itens, com ITEM_UNDO já
aplicado) é preenchida por `python -m src.etl.load_items` a partir das
timelines brutas — rode após qualquer coleta nova. O catálogo de itens
(`data/items.json`) vem do Data Dragon; a página de campeão usa os dois
para a seção "Itens finalizados mais construídos".

```bash
python -m src.models.export_model     # uma vez (habilita o /predict)
uvicorn src.api.main:app --port 8000  # terminal 1 — API
cd frontend && npm install            # primeira vez
npm run dev                           # terminal 2 — http://localhost:5173
```

## Dimensionamento da coleta (chave de dev: 100 req/2min)

| Partidas | Requisições (match+timeline) | Tempo aproximado |
|---------:|-----------------------------:|-----------------:|
| 1.000    | ~2.000                       | ~40 min          |
| 10.000   | ~20.000                      | ~7 h             |
| 30.000   | ~60.000                      | ~20 h            |

A coleta é retomável: partidas já salvas são puladas. Rode em sessões
diárias (a chave expira em 24h) ou solicite uma **Personal API Key** no
portal da Riot (limites maiores, sem expiração diária).

## Decisões importantes a registrar no TCC 2

- **Tarefa de predição**: este scaffold implementa predição *em jogo*
  (estado aos 15 min, como Hodge et al., 2021). Alternativa: predição
  *pré-jogo* por composição — exigiria outras features. Documente a escolha.
- **Vazamento de dados**: nunca usar estatísticas finais da partida como
  feature. Ver aviso em `src/features/build_features.py`.
- **Métricas**: acurácia, precisão, recall, F1 e AUC-ROC implementadas
  (conforme ficha de avaliação); considere curva de calibração.
- **Validação da interface NL** (apontamento da banca): benchmark de
  perguntas de referência com *execution accuracy* em `src/nlq/evaluate_nlq.py`
  — expanda para >= 20 perguntas no TCC II.

## Próximas etapas (mapeadas aos objetivos específicos)

- [x] (a, b, c) Coleta, schema e ETL — este scaffold
- [x] (d) EDA inicial — `notebooks/01_eda.py`
- [x] (e) Baseline RF/XGBoost/MLP — `src/models/train_baseline.py`
- [x] (g) Interface NL text-to-SQL com validação de segurança — `src/nlq/`
- [x] (g) Metodologia de validação da interface NL — `src/nlq/evaluate_nlq.py`
- [x] (f) API FastAPI com endpoints para dashboards — `src/api/main.py`
- [x] (e) Explicabilidade com SHAP — `src/models/explain_shap.py`
- [x] (f) Dashboard interativo Streamlit com consulta NL — `src/dashboard/app.py`
- [x] (e) Tuning de hiperparâmetros (GridSearchCV) — `src/models/tune_models.py`
- [x] Rodar tudo com dados reais (10,4k partidas; métricas em
      `docs/diario_execucao.md`, entrada de 2026-07-03)
- [x] (f) Front end React como interface principal — `frontend/`
- [ ] Escrever os capítulos do TCC II a partir de `docs/diario_execucao.md`
