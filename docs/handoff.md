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

1. **Solo queue** (Riot API): partidas ranqueadas de elo alto (Challenger/GM/Master)
   multi-região (BR1/EUW1/KR/NA1, mais um resíduo EUN1, fila 420) —
   **41.063 partidas** no banco (BR1 11.936, EUW1 11.744, KR 10.204,
   NA1 7.159, EUN1 20) e **39.188 linhas** na base do modelo preditivo
   (corte de 15 min, retreino de 2026-10-04). A coleta foi retomável ao
   longo de todo o projeto: 10.295 em julho, 23.133 em 2026-07-06,
   24.154 em 2026-09-28, 33.713 em 2026-10-03 e 39.426 em 2026-10-04,
   quando a NA1 foi de 1.446 para 7.159, fechando em 41.063 com a
   última rodada da KR.
   **Dois números coexistem de propósito:** a análise descritiva (Quadro
   1, viés de lado, teste de faixa de duração) usa as 41.063;
   *features* e modelos foram congelados nas 39.426 e não foram
   retreinados — a diferença de 1.637 partidas é limitação declarada
   (das 1.754 partidas sem *features*, 1.647 são da KR e 107 são de
   BR1, EUW1 e NA1; as features cobrem 39.309 partidas distintas)
   na Seção 6.1 do TCC (detalhe no Apêndice F). JSON bruto + timelines guardados para
   reprocessamento.
2. **Competitivo** (Oracle's Elixir): **99.259 jogos** profissionais de
   2014-2026 (LCK/LPL/LEC/LTA/CBLOL etc.), carregados de CSVs anuais.
   Contagem por `game_id` distinto — `pro_games` guarda duas linhas por
   jogo (uma por time), então `COUNT(*)` devolve o dobro.

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
  tune_models_full, export_model, explain_shap). Produção:
  XGBoost n=500/lr=0.01/depth=3 por fase em `data/models_phases.joblib`,
  retreinado em **39.188 linhas** (corte de 15 min, 2026-10-04) — ver
  números abaixo.
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
  perguntas, exigência da banca; grava `reports/nlq_benchmark.json` com
  accuracy, base, modelo e o desfecho de cada pergunta, e **recusa gravar
  em run degenerado** — sem chave, com accuracy abaixo de 50% ou com três
  ou mais falhas de mesma causa — para não sobrescrever a última medição
  boa com um 0/26).
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

Modelo em produção, solo queue **39.188 partidas** no corte de 15 min
(retreino de 2026-10-04 — números do CV 5-fold com semente 42 e
hiperparâmetros de produção 500/0,01/3; o `GridSearchCV` sobre as 39 mil
linhas devolveu ajuste equivalente, 200 árvores a taxa 0,05, o que
confirma que a limitação de taxa-base registrada na Seção 6.1 e no Apêndice F do TCC não
é subajuste):

| Modelo | Acurácia | Precisão | Recall | F1 | AUC-ROC |
|---|---|---|---|---|---|
| XGBoost (produção) | 0,7621 | 0,7561 | 0,7228 | 0,7391 | 0,8473 |
| MLP | 0,7610 | 0,7537 | 0,7239 | 0,7385 | 0,8455 |
| RandomForest | 0,7457 | 0,7330 | 0,7150 | 0,7239 | 0,8277 |

(Números exatos, não aproximados: 0,7610 arredonda para 0,76 e 0,7457 para
0,75 — escrever "~0,74" subestimava o MLP.) Reproduz com
`.venv\Scripts\python.exe -m src.models.multi_cutoff_metrics`, que cobre
os **4 cortes × 3 modelos** do Apêndice C e grava
`reports/metricas_corte.json`. Esse JSON é o que
`python docs/verifica_tcc.py` confronta com os números citados no texto —
é por ele que um número velho no TCC é detectado em vez de passar.
`train_baseline.py` continua sendo só o corte de 15 min.

NLQ: **88% execution accuracy** (23/26, medido repetidamente e estável
nesta sessão de revisão — 2026-07-13; as 3 falhas são a mesma família
benigna de sempre, formatação/coluna extra, não erro real). 26
perguntas de referência (22 solo queue + 4 competitivo).

**Achados de tese (os dois lados do viés de lado):**
- Solo queue Challenger/GM de elo alto: **o vermelho vence mais que o azul
  em TODAS as regiões com amostra relevante** — medido em SQL sobre 24.154
  partidas em 2026-09-28: BR1 56,3% (11.936), EUW1 53,8% (6.281), KR 50,2%
  (4.471), NA1 51,9% (1.446); EUN1 (20 partidas) fica fora por amostra
  insuficiente. Ou seja: **não é um fato do Brasil**, é um padrão de elo
  muito alto em geral — a formulação antiga ("vermelho vence 56,3% no
  BR") foi superada por esta leitura regionalizada e não deve voltar ao
  texto (o próprio TCC adverte, Seção 5.3). A direção do achado se
  manteve idêntica à leitura original de 2026-07-06; ver diário
  2026-09-28.
- **E O VIÉS É CONSTANTE POR FASE** — resultado de 2026-10-04, que
  substitui e refuta o achado de 2026-07-08. Entre partidas genuinamente
  empatadas (|diferença de ouro| < 500) a taxa de vitória do azul é 46,4%
  (10min, n=7.349), 47,9% (15min, n=3.970), 46,7% (20min, n=2.423) e 47,1%
  (25min, n=1.430). Dispersão de 1,4 pp e **nenhuma diferença entre pares
  sobrevive ao ajuste de Holm** (menor p corrigido = 0,83). Os ICs de 95% se
  sobrepõem: as quatro taxas são indistinguíveis, e o corte mais vermelho
  é o de 10 min, não o de 15. O que a amostra maior desfez foi a
  *evolução* atribuída ao viês, não o viês — que segue forte: o IC
  do corte de 10 min é [45,3%, 47,6%], que exclui 50% com folga.
  Mede com `python docs/testa_diferenca_taxas.py`; a bateria
  (`tests/validate_predictions.py`) cobra a constância, não o pico.
- Competitivo (**99.259 jogos**, 2014-2026): **azul vence 53,2%**.
  A série anual é estável a partir de 2016 (52,5% a 55,0%); 2014
  (58,2%) e 2015 (55,3%) divergem sobre amostras de 814 e 1.702 jogos,
  contra 99.259 no total.
  Hipótese documentada: counter-pick garantido (solo queue) vs
  prioridade de primeiro pick (pro).
- Conversão de vantagem: com +2k a +4k de ouro aos 15, o azul vence
  81,5% no pro (n=3.294) contra 73,7% no solo queue (n=5.166) — "macro
  ganha jogo", quantificado. Diferença de 7,8 pp, z = 8,28. A faixa
  +4k a +6k no pro apoia-se em só 72 jogos e é indicativa. O valor
  antigo (84,0% vs ~68%, medido sobre ~12k partidas) era o dobro do
  efeito real. Mede com `python docs/confere_conversao_advantagem.py`.
- SHAP por fase: torres ficam em ~0 nos três primeiros cortes (0,0044 /
  0,0060 / 0,0031) e saltam para 0,0928 aos 25 min — 15x entre 15 e 25.
  A série **não é monôtona** (20 min é menor que 10 e 15): é
  concentração tardia, não crescimento contínuo. As placas caem
  aos 14 min, razão de existir um modelo por fase.
- **11 experimentos de melhoria do modelo, todos ≈zero** (barão/arauto,
  dispersão de time, tuning por fase, calibração extra, ouro em itens,
  split def/off, dragões por tipo, item_gold_diff refeito,
  ward_diff/ward_kill_diff, placas de torre, percentis comportamentais do
  jogador): a abordagem atual está no teto do que features agregadas de
  estado (e até um eixo comportamental de fonte diferente) permitem —
  material para a seção de limitações. O 11º (`teamwork_pct_diff`/
  `expertise_pct_diff`, diário 2026-10-05) é o único que não vem da
  *timeline* — vem de `lol-challenges-v1`, testado sobre partidas KR
  recentes pra evitar vazamento do estado vitalício do jogador; um piloto
  pequeno (n=199) sugeriu sinal (+0,009 de delta) que não se sustentou ao
  escalar para n=2.987 (-0,0031) — regressão à média, não achado. A
  contagem é 11 e não 9 porque os experimentos de placas de torre
  (`plate_diff`) e percentis comportamentais entraram na série por
  último; e não é 8 porque o experimento de dragões por tipo
  (`monsterSubType`, diário 2026-07-05) entrou antes deles e ficou de
  fora do Apêndice K do TCC até 2026-10-03; o "7º"/"8º" nos títulos das
  entradas de 2026-07-06 do diário é renumeração local que ignora esses
  três experimentos.
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
de escopo, não uma lista de pendências ativas.

**O TCC II está escrito e fechado (2026-10-04), revisado ponta a ponta
em 2026-10-05 (Blocos A-E, ver diário).** `docs/tcc2_texto.md`
→ `docs/build_tcc_docx.py` → `docs/tcc2_final.docx`. **29 páginas** do
Resumo (página 1) ao fim das Referências, limite 30 (régua corrigida em
2026-10-23; a antiga parava no início das Referências e dizia "30" quando
eram 37). Reduzido em 2026-10-28 conforme `docs/plano_reducao_corpo.md`,
com 6 quadros e 5 figuras recortadas no corpo a pedido do orientador
(`docs/capturar_figuras_texto.py`). 31 referências, Apêndices A-K (G a K novos em 2026-11-03; em 2026-11-04 o antigo I saiu e o antigo D
foi fundido no de precisão; E = telas inteiras, F = limitações em detalhe), Anexo A (documentação da Riot).
O Apêndice D recebeu as notas de proveniência da Seção 5.3, movidas do
corpo em 2026-10-20 para abrir espaço às citações novas). Suíte completa verde:
`tests/smoke_test.py`, `tests/validate_predictions.py` (aprovado com
ressalvas), `docs/verifica_tcc.py` (22 checagens, consistente),
`docs/confere_docx.py` (conforme), `frontend` lint + 31/31 testes.
Nenhuma pendência de texto em aberto — ver a seção "Pendências finais
antes da entrega" no fim de `docs/tcc2_texto.md` para o histórico
completo das decisões (título acadêmico, posição de "Trabalhos
Relacionados", formatação herdada do TCC I).

Pendências reais atuais, nenhuma delas bloqueando a entrega do TCC
(ver "Próximos registros pendentes" no fim de `diario_execucao.md`):
- Champion select competitivo no Team Builder (única feature da visão
  original ainda não iniciada — é produto, não é exigência do TCC).
- `monotone_constraints` no XGBoost — só se a banca cobrar
  monotonicidade formal; não é bug, é característica documentada.
- Competitivo/pro-play: enriquecimentos adicionais adiados (opções já
  levantadas em `project_scope_decisions.md` na memória do assistente).
