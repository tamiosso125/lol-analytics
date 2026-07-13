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

1. **Solo queue** (Riot API): partidas ranqueadas Challenger/GM
   multi-região (BR1/EUW1/KR/NA1, fila 420) — **23.133 partidas**
   (2026-07-06, coleta retomável), com JSON bruto + timelines
   guardados para reprocessamento.
2. **Competitivo** (Oracle's Elixir): ~99k jogos profissionais de
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
`/compose` (aba Composição do Simulador) é heurística de win rates
históricos, deliberadamente separada do modelo ML e sinalizada como
tal na UI.

## Onde estão as coisas

- **Schema**: `db/schema.sql` — solo queue (`players`, `raw_*`,
  `matches`, `teams`, `participants`, `bans`, `item_events`, `items`
  — catálogo Data Dragon, 2026-07-10, pra JOIN de nome de item) +
  competitivo (`pro_games`, `pro_players`).
- **Coleta**: `src/collect/` — `seed_players`/`collect_matches`
  (Riot API, chave dev expira em 24h, multi-região via
  `--platforms`), `backfill_names`, `collect_pro` (Oracle's Elixir; o
  Drive público tem quota diária — fallback é baixar manualmente para
  `data/pro/`; já usado com sucesso, não é um bloqueio ativo).
- **ETLs**: `src/etl/` — `load_matches` (normalização match-v5),
  `load_items` (compras/vendas/ITEM_DESTROYED com ITEM_UNDO aplicado;
  TRUNCATE+rebuild; rodar após coleta nova), `load_item_catalog`
  (catálogo `items` a partir de `data/items.json`; roda só quando a
  versão do Data Dragon muda), `load_pro` (CSVs do OE; idempotente por
  ano).
- **Features/modelos**: `src/features/build_features.py` (CUTOFFS
  10/15/20/25), `src/models/` (train_baseline, tune_models,
  export_model, explain_shap). Produção: XGBoost n=500/lr=0.01/depth=3
  por fase em `data/models_phases.joblib`, retreinado em 23.133
  partidas (2026-07-06) — ver números abaixo.
- **API**: `src/api/main.py` — todos os endpoints (stats solo queue,
  `/stats/pro/*` com `?year=` padrão mais-recente, análise de partida
  com estado por minuto, heat map/posições, itens por campeão,
  `/compose`, `/predict`, `/coach` + `/coach/draft`, NLQ). Lista
  completa em `docs/scripts.md`.
- **Coach** (`src/coach/`): `advice.py` — orientação estratégica via
  LLM (Claude Haiku) em cima do estado+SHAP já calculados, com 3
  camadas opcionais de contexto real (composição/matchup/sinergia;
  itens+posição+visão+momentum da timeline; nada é invenção — todo
  "dado real" citado vem de uma query, não de memória do modelo) +
  leitura de draft pré-jogo (`generate_draft_analysis`, sem estado de
  jogo) + sugestão de build estruturada com ícones reais de item
  (nome resolvido contra `items`, nunca confiado à LLM). Ver
  `project_scope_decisions.md` na memória do assistente pro histórico
  completo das 4 camadas.
- **NLQ**: `src/nlq/` — `nl_to_sql.py` (aceita `SELECT` e `WITH ...
  SELECT`/CTE desde 2026-07-10), `schema_context.py` (⚠️ regra:
  qualquer mudança aqui exige re-rodar `evaluate_nlq` — já regrediu
  silenciosamente mais de uma vez), `evaluate_nlq.py` (benchmark, 26
  perguntas, exigência da banca).
- **Front**: `frontend/` — 6 páginas desde a consolidação de
  2026-07-06: Início, Dashboard, Campeões (+detalhe com itens),
  Partidas (+análise com heat map, itens/KDA/ouro/CS/dano por minuto,
  modo "e se", leitura de draft, replay sincronizado), Competitivo
  (seletor de ano), Consulta NL, Simulador (3 abas: Composição —
  antiga Montar Partida, com jogadores opcionais —, Estado — antiga
  Predição —, Explicabilidade). Rotas antigas (`/montar`, `/predicao`,
  `/explicabilidade`) redirecionam para `/simulador`.
- **Testes**: `tests/smoke_test.py` (roda em tempdir — NÃO toca dados
  reais) e `tests/validate_predictions.py` (bateria comportamental do
  modelo de produção); front tem Vitest (`frontend/npm run test`,
  31 testes) + ESLint.
- **Docs**: `diario_execucao.md` (fonte primária para escrever o TCC),
  `scripts.md` (referência), `planejamento_v2.md` (plano de sprints —
  **todos os 6 sprints já entregues**, ver diário; mantido como
  registro histórico da decisão, não uma lista de pendências ativas).
- **Memória do assistente** (Claude Code): contexto persistente em
  `C:\Users\Home\.claude\projects\...\memory\` — lido automaticamente.

## Números que importam (para o texto do TCC)

Modelo em produção, solo queue **23.133 partidas** (retreino final
2026-07-06 — números do `train_baseline` CV 5-fold no corte de 15min;
hiperparâmetros são os tunados na base de 10k por `tune_models.py`,
reaplicados ao volume maior via `export_model.py`; não houve um novo
GridSearchCV completo em 23k — se a banca cobrar isso, é reproduzível):

| Modelo | Acurácia | AUC-ROC |
|---|---|---|
| XGBoost (produção) | 0,7573 | 0,8393 |
| MLP | ~0,74 | 0,8385 |
| RandomForest | ~0,73 | 0,8219 |

(MLP/RF são do mesmo retreino, ver `docs/diario_execucao.md`
2026-07-06 pra tabela completa com os 4 cortes de fase.)

NLQ: **88% execution accuracy** (23/26, medido repetidamente e estável
nesta sessão de revisão — 2026-07-13; as 3 falhas são a mesma família
benigna de sempre, formatação/coluna extra, não erro real). 26
perguntas de referência (22 solo queue + 4 competitivo).

**Achados de tese (os dois lados do viés de lado):**
- Solo queue Challenger/GM BR: **vermelho vence 56,3%** no agregado —
  mas **NÃO é constante por fase** (achado 2026-07-08, não repetir a
  versão simplificada em texto): a probabilidade-base do modelo pra
  partidas empatadas sobe de 47,8% (10min) a 51,1% (25min) — mais
  favorável ao vermelho cedo, quase neutro tarde. Testado 3 formas
  (win rate bruto de partidas empatadas, restrito a BR1, duração total
  sem filtro de empate) — a tendência de enfraquecimento é sólida, mas
  a amostra de "empatado aos 25min" é pequena (IC ainda inclui viés
  vermelho) — não afirmar uma inversão completa confirmada. Ver diário
  2026-07-08 pra tabela e metodologia completas.
- Competitivo (~99k jogos): **azul vence ~53%**, estável ATRAVÉS DOS
  ANOS — a literatura descreve o pro; nosso solo queue é o outlier.
  Hipótese documentada: counter-pick garantido (solo queue) vs
  prioridade de primeiro pick (pro).
- Conversão de vantagem: com +2k a +4k de ouro aos 15, o pro vence
  84,0% vs ~68% no solo queue — "macro ganha jogo", quantificado.
- SHAP por fase: torres saem de ~0 (10-15 min) para dezenas de vezes
  mais importância aos 25 (as placas caem aos 14) — razão de existir
  um modelo por fase.
- **8 experimentos de melhoria do modelo, todos ≈zero** (barão/arauto,
  dispersão de time, tuning por fase, calibração extra, ouro em itens,
  split def/off, item_gold_diff refeito, ward_diff/ward_kill_diff):
  a abordagem atual está no teto do que features agregadas de estado
  permitem — material para a seção de limitações.
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
`export_model` + restart da API. `load_item_catalog` só precisa rodar
de novo se `data/items.json` mudar de versão (não depende de coleta).

## Limitações conhecidas (documentar, não "consertar às pressas")

- Amostras pequenas em matchups/sinergias específicos — NLQ avisa e
  rotula "Leitura de jogo"; shrinkage de dupla (com IC) já shipped
  (2026-07-06), ver `team_synergies()`.
- Benchmark NLQ tem 3 falhas benignas aceitas (formatação, não erro)
  — deliberadamente não superajustado; 23/26 = 88%.
- Cobertura por patch desigual no solo queue (16.13 domina) — exposto
  no Dashboard.
- Wave/micro state não existe em nenhuma API da Riot — caminhos reais
  (replays .rofl, CV no minimapa) pesquisados e documentados no diário
  como trabalhos futuros; o modo "e se" responde contrafactuais de
  ESTADO, não de ação.
- Monotonicidade isolada de kill/tower_diff imperfeita (fatores
  redundantes/raros) — característica documentada na bateria de
  validação, `monotone_constraints` é opção se a banca cobrar.
- Champion select competitivo no Simulador/Team Builder — único item
  pendente da visão original que ainda não foi iniciado (ver
  `project_team_builder.md` na memória do assistente).

## Próximos passos

`docs/planejamento_v2.md` está **100% entregue** (sprints 0-6, ver
diário 2026-07-05/06) — mantido só como registro histórico da decisão
de escopo, não uma lista de pendências ativas. Pendências reais atuais
(ver "Próximos registros pendentes" no fim de `diario_execucao.md`,
seção sempre mantida atualizada):
- Escrever os capítulos do TCC a partir do diário (maior pendência
  real) — inclui atualizar as tabelas de métrica com os números de
  23k partidas (2026-07-06) e o achado de viés de lado por fase
  (2026-07-08), não os números antigos de 10k.
- Champion select competitivo no Team Builder (única feature da visão
  original ainda não iniciada).
- Ampliar mais a amostra por região (KR/EUW1/NA1 ainda bem menores
  que BR1) se quiser reforçar o achado de viés de lado.
- `monotone_constraints` no XGBoost — só se a banca cobrar
  monotonicidade formal; não é bug, é característica documentada.
