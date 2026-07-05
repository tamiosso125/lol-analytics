# Handoff — Bellestraiko (TCC II)

Documento para quem retomar o projeto "a frio" — resume o que existe,
por que existe, o que falta e onde olhar. Não repete o histórico
cronológico (`docs/diario_execucao.md`), a referência de scripts
(`docs/scripts.md`) nem o plano de próximos passos
(`docs/planejamento_v2.md`) — é o mapa que aponta para os três.

> Nome: renomeado 2× em 2026-07-03 — "LoL Analytics" colidia com
> lolalytics.com e "Hextech Lab" com um canal do YouTube. Nome atual:
> **Bellestraiko**. O diretório do repo continua `lol-analytics`.

## O que é o projeto

TCC II (CS, Unisinos): plataforma de análise de esports de League of
Legends com DOIS datasets complementares:

1. **Solo queue** (Riot API): partidas ranqueadas Challenger/GM BR
   (fila 420) — ~11,8k partidas e crescendo (coleta retomável), com
   JSON bruto + timelines guardados para reprocessamento.
2. **Competitivo** (Oracle's Elixir): 99.259 jogos profissionais de
   2014-2026 (LCK/LPL/LEC/LTA/CBLOL etc.), carregados de CSVs anuais.

Sobre eles: modelos de predição de vitória "em jogo" por fase
(10/15/20/25 min), interface de perguntas em linguagem natural
(text-to-SQL com validação), e um front React com análises que sempre
carregam o "porquê" junto do número.

## Arquitetura (visão rápida)

```
Riot API → coletor rate-limited → raw_matches/raw_timelines (JSONB)
                                        │ ETLs
                                        ▼
        matches/teams/participants/players/bans/item_events
                                        │
Oracle's Elixir CSVs → data/pro/ → pro_games/pro_players
                                        │
          ┌─────────────────────────────┼──────────────────────┐
          ▼                             ▼                      ▼
  features por fase             modelos XGBoost         API FastAPI (main.py)
  (build_features.py)           por fase                       │
                                (export_model.py)              ▼
                                                    frontend/ React (principal)
                                                    + Streamlit (alternativa)
```

Decisões centrais: predição usa SÓ estado pré-corte da timeline (nunca
totais finais — vazamento de dados; aviso em `build_features.py`); o
`/compose` do Montar Partida é heurística de win rates históricos,
deliberadamente separada do modelo ML e sinalizada como tal na UI.

## Onde estão as coisas

- **Schema**: `db/schema.sql` — solo queue (`players`, `raw_*`,
  `matches`, `teams`, `participants`, `bans`, `item_events`) +
  competitivo (`pro_games`, `pro_players`).
- **Coleta**: `src/collect/` — `seed_players`/`collect_matches`
  (Riot API, chave dev expira em 24h), `backfill_names`, `collect_pro`
  (Oracle's Elixir; o Drive público tem quota diária — fallback é
  baixar manualmente para `data/pro/`).
- **ETLs**: `src/etl/` — `load_matches` (normalização match-v5),
  `load_items` (compras/vendas com ITEM_UNDO aplicado; TRUNCATE+rebuild;
  rodar após coleta nova), `load_pro` (CSVs do OE; idempotente por ano).
- **Features/modelos**: `src/features/build_features.py` (CUTOFFS
  10/15/20/25), `src/models/` (train_baseline, tune_models,
  export_model, explain_shap). Produção: XGBoost n=500/lr=0.01/depth=3
  por fase em `data/models_phases.joblib`.
- **API**: `src/api/main.py` — todos os endpoints (stats solo queue,
  `/stats/pro/*` com `?year=` padrão mais-recente, análise de partida
  com estado por minuto, heat map/posições, itens por campeão,
  `/compose`, `/predict`, NLQ). Lista completa em `docs/scripts.md`.
- **NLQ**: `src/nlq/` — `nl_to_sql.py`, `schema_context.py` (⚠️ regra:
  qualquer mudança aqui exige re-rodar `evaluate_nlq` — já regrediu
  silenciosamente 2×), `evaluate_nlq.py` (benchmark, exigência da
  banca).
- **Front**: `frontend/` — páginas: Início, Dashboard, Campeões
  (+detalhe com itens), Partidas (+análise com heat map, objetivos por
  minuto e modo "e se"), Competitivo (seletor de ano), Consulta NL
  (Explicação como aba padrão), Predição, Montar Partida (combobox de
  busca, estado opcional combinado ao ML), Explicabilidade.
- **Testes**: `tests/smoke_test.py` (roda em tempdir — NÃO toca dados
  reais) e `tests/validate_predictions.py` (bateria comportamental do
  modelo de produção).
- **Docs**: `diario_execucao.md` (fonte primária para escrever o TCC),
  `scripts.md` (referência), `planejamento_v2.md` (próxima fase, 8
  sprints).
- **Memória do assistente** (Claude Code): contexto persistente em
  `C:\Users\Home\.claude\projects\...\memory\` — lido automaticamente.

## Números que importam (para o texto do TCC)

Modelos tunados, solo queue 10k+ (logs em `reports/*_10k.log`):

| Modelo | Acurácia | AUC-ROC |
|---|---|---|
| MLP | 0,7522 | 0,8325 |
| XGBoost (produção) | 0,7501 | 0,8319 |
| RandomForest | 0,7507 | 0,8305 |

NLQ: **91-95% execution accuracy** (flutua entre execuções; 22
perguntas; citar a faixa, não um número cravado; re-medir ao escrever).

**Achados de tese (os dois lados do viés de lado):**
- Solo queue Challenger/GM BR: **vermelho vence 56,3%** (estável entre
  patches) — contraria a literatura.
- Competitivo (99k jogos): **azul vence ~53%**, estável ATRAVÉS DOS
  ANOS — a literatura descreve o pro; nosso solo queue é o outlier.
  Hipótese documentada: counter-pick garantido (solo queue) vs
  prioridade de primeiro pick (pro).
- Conversão de vantagem: com +2k a +4k de ouro aos 15, o pro vence
  84,0% vs ~68% no solo queue — "macro ganha jogo", quantificado.
- SHAP por fase: torres saem de ~0 (10-15 min) para dezenas de vezes
  mais importância aos 25 (as placas caem aos 14) — razão de existir
  um modelo por fase.
- **6 experimentos de melhoria do modelo, todos ≈zero** (barão/arauto,
  dispersão de time, tuning por fase, calibração extra, ouro em itens,
  split def/off): a abordagem atual está no teto do que features
  agregadas de estado permitem — material para a seção de limitações.
- Validação externa: o próprio Oracle's Elixir publica uma calculadora
  de win probability early-game com a mesma estrutura da nossa
  Predição.

## Como rodar

```bash
# API (terminal 1)           # front (terminal 2)
uvicorn src.api.main:app     cd frontend && npm run dev
  --reload --port 8000       # http://localhost:5173
```

Pré-requisitos: Postgres com schema (`python -m src.db`), `.env`
(RIOT_API_KEY 24h, DATABASE_URL, ANTHROPIC_API_KEY). Ordem completa de
pipeline no README. Após coleta nova: `load_items` + `build_features` +
`export_model` + restart da API.

## Limitações conhecidas (documentar, não "consertar às pressas")

- Amostras pequenas em matchups/sinergias específicos — NLQ avisa e
  rotula "Leitura de jogo"; shrinkage formal é o sprint 4 do plano.
- Benchmark NLQ tem 1-2 falhas benignas aceitas (formatação, não erro)
  — deliberadamente não superajustado.
- Cobertura por patch desigual no solo queue (16.13 domina) — exposto
  no Dashboard.
- Wave/micro state não existe em nenhuma API da Riot — caminhos reais
  (replays .rofl, CV no minimapa) pesquisados e documentados no diário
  como trabalhos futuros; o modo "e se" responde contrafactuais de
  ESTADO, não de ação.
- Monotonicidade isolada de kill/tower_diff imperfeita (fatores
  redundantes/raros) — característica documentada na bateria de
  validação, `monotone_constraints` é opção se a banca cobrar.

## Próximos passos

Seguir `docs/planejamento_v2.md` (8 sprints): sprint 0 = pedir a
Personal API Key da Riot (aprovação demora); sprint 1 = competitivo em
tudo (NLQ, campeão); sprint 2 = modelo pro + tipos de dragão; sprints
3-4 = perfis de jogador + Montar Partida com shrinkage; sprint 5 =
multi-região; sprint 6 = MVP tempo real (replay-ao-vivo); 7+ pós-TCC.
Em paralelo: escrever os capítulos do TCC a partir do diário.
