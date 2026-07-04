# Documentação dos scripts

Referência de cada script do projeto: o que faz, como rodar, o que lê e o
que produz. Complementa a "Ordem de execução" do `README.md` com mais
detalhe técnico. Para o histórico de execuções e resultados, ver
`docs/diario_execucao.md`.

Nota sobre `.pyc`: as pastas `__pycache__/` e os arquivos `.pyc` que
aparecem ao lado de cada módulo são bytecode compilado pelo Python — um
cache binário gerado automaticamente, não código-fonte. Não abra esses
arquivos; edite sempre o `.py` correspondente. Eles já estão no
`.gitignore` e podem ser apagados a qualquer momento sem problema (o
Python os regera sozinho).

---

## Configuração e conexão

### `src/config.py`
Lê variáveis do `.env` (via `python-dotenv`) e expõe `RIOT_API_KEY`,
`RIOT_PLATFORM`, `RIOT_REGION`, `DATABASE_URL`. Não é executável — é
importado por praticamente todos os outros módulos.

### `src/db.py`
- `get_conn()`: abre uma conexão psycopg2 usando `DATABASE_URL`.
- `init_schema()`: lê `db/schema.sql` e aplica no banco.

**Uso:** `python -m src.db` — cria as tabelas (`players`, `raw_matches`,
`raw_timelines`, `matches`, `teams`, `participants`). Idempotente
(`CREATE TABLE IF NOT EXISTS`), seguro rodar de novo.

---

## Coleta (`src/riot/`, `src/collect/`)

### `src/riot/client.py`
`RiotClient`: wrapper HTTP sobre a Riot API com rate limiting (janela
deslizante de 95 req/2min, abaixo do limite real de 100) e retry em
429/5xx. Métodos: `challenger_league`, `grandmaster_league`,
`match_ids_by_puuid`, `match`, `timeline`. Não é executável diretamente.

### `src/collect/seed_players.py`
Busca os ladders Challenger e Grandmaster (fila 420) na Riot API e faz
upsert na tabela `players` (puuid, tier, liga, pontos).

**Uso:** `python -m src.collect.seed_players`
**Lê:** Riot API (`challengerleagues`, `grandmasterleagues`).
**Escreve:** tabela `players`.

### `src/collect/backfill_names.py`
Preenche `game_name`/`tag_line` dos jogadores via account-v1 (o endpoint
de liga não retorna mais nomes, só puuid). Uma requisição por jogador,
respeitando o rate limit; processa só quem ainda está sem nome.

**Uso:** `python -m src.collect.backfill_names --min-games 20`
**Lê:** tabelas `players`/`participants`; Riot API (account-v1).
**Escreve:** colunas `game_name`/`tag_line` de `players`.

### `src/collect/collect_matches.py`
Para os N jogadores com mais LP em `players`, busca os últimos
match_ids (fila 420) e baixa match + timeline de cada um que ainda não
está no banco. JSON bruto vai para `raw_matches`/`raw_timelines`; cada
partida é normalizada na hora via `load_one` (ETL).

**Uso:** `python -m src.collect.collect_matches --players 730 --matches-per-player 40`
(flags: `--players` N de jogadores a considerar, `--matches-per-player`
quantos match_ids recentes buscar por jogador, `--no-timeline` para pular
o download da timeline).
**Lê:** tabela `players`; Riot API (match-v5 ids/match/timeline).
**Escreve:** `raw_matches`, `raw_timelines`, e (via ETL) `matches`,
`teams`, `participants`.
**Retomável:** pula match_ids já presentes em `raw_matches` — pode ser
rodado várias vezes para ampliar a coleta.

---

## ETL

### `src/etl/load_matches.py`
- `load_one(conn, match)`: normaliza um JSON de partida (match-v5) nas
  tabelas relacionais, incluindo os bans de cada time (bans com
  championId -1, "sem ban", são ignorados). Descarta remakes
  (`gameDuration < 300s`).
- `reprocess_all()`: reprocessa tudo que já está em `raw_matches` (útil
  se o schema relacional mudar sem precisar recoletar da Riot API).
  Usa duas conexões: cursor nomeado (server-side) exige transação, então
  a leitura é transacional e a escrita autocommit.

**Uso:** `python -m src.etl.load_matches` (reprocessa tudo; idempotente
via ON CONFLICT DO NOTHING). Durante a coleta normal, `load_one` já é
chamado automaticamente por `collect_matches.py`.

### `src/collect/collect_pro.py`
Baixa os CSVs anuais de partidas COMPETITIVAS (pro play) do Oracle's
Elixir (fonte padrão em trabalhos acadêmicos de LoL; 12 linhas por jogo
— 10 jogadores + 2 times — com gold/xp/cs diff aos 15 min). Os arquivos
ficam num Google Drive público com QUOTA diária: quando estourada, o
script avisa e o fallback é baixar manualmente em
oracleselixir.com/tools/downloads para `data/pro/`.

**Uso:** `python -m src.collect.collect_pro --year 2026`
**Escreve:** `data/pro/{ano}_LoL_esports_match_data_from_OraclesElixir.csv`

### `src/etl/load_pro.py`
Carrega os CSVs de `data/pro/` nas tabelas `pro_games` (linhas de time)
e `pro_players` (linhas de jogador). Idempotente por ano (DELETE do ano
antes de inserir). Linhas sem game_id são descartadas; ligas que não
reportam os cortes de 15 min ficam com essas colunas NULL.

**Uso:** `python -m src.etl.load_pro [--year 2026]`
**Lê:** `data/pro/*.csv`. **Escreve:** `pro_games`, `pro_players`.

### `src/etl/load_items.py`
Extrai as compras/vendas de itens dos eventos ITEM_* das timelines para
a tabela `item_events` (~2,4M linhas em 10k partidas). Os `ITEM_UNDO`
são aplicados no ETL (a compra desfeita não entra — a tabela reflete o
que o jogador manteve, não cada clique na loja); `ITEM_DESTROYED`
(componente fundido em receita, consumível usado) não é gravado. Só
processa timelines cuja partida existe em `matches` (raw_timelines tem
remakes que o ETL principal pula — sem o filtro, viola a FK). A tabela
é reconstruída do zero a cada execução (TRUNCATE) — rodar após
qualquer coleta nova. O catálogo `data/items.json` (nome, custo, tags,
receitas por item_id) vem do Data Dragon
(`cdn/16.13.1/data/pt_BR/item.json`, versão fixada em sincronia com o
helper `itemIcon` do front) — a API o carrega no startup e deriva a
lista de "itens finalizados" (nada constrói a partir dele, comprável,
custo >= 1100, não consumível/trinket, válido no mapa 11).

**Uso:** `python -m src.etl.load_items`
**Lê:** `raw_timelines`, `matches`. **Escreve:** `item_events`.
**Lê:** `raw_matches`.
**Escreve:** `matches`, `teams`, `participants`, `bans`.

---

## Features

### `src/features/build_features.py`
Extrai features de estado da partida em MÚLTIPLOS cortes de tempo
(10/15/20/25 min — fase de rotas ao late game; ver `CUTOFFS`) a partir
de `raw_timelines`, evitando vazamento de dados (não usa estatísticas
finais da partida). `features_from_timeline(payload, cutoff_min)` é
reutilizável para qualquer minuto (usada pela análise de partida da API).

**Uso:** `python -m src.features.build_features`
**Lê:** `raw_timelines` + `teams` (para o rótulo `blue_win`).
**Escreve:** `data/features_phases.csv` (todos os cortes, coluna
`cutoff_min`) e `data/features.csv` (só o corte de 15 — compatível com
train_baseline/tune_models/gold15).

---

## Modelos

### `src/models/train_baseline.py`
Compara RandomForest, XGBoost e MLP (hiperparâmetros fixos, não
tunados) via validação cruzada estratificada (5 folds). Reporta as 5
métricas exigidas pela banca: acurácia, precisão, recall, F1, AUC-ROC.

**Uso:** `python -m src.models.train_baseline`
**Lê:** `data/features.csv`.
**Escreve:** apenas stdout (tabela de métricas).

### `src/models/tune_models.py`
Busca em grade (`GridSearchCV`, otimizando AUC-ROC) de hiperparâmetros
para os 3 modelos, com a mesma validação cruzada do baseline. Reporta as
5 métricas com os melhores parâmetros de cada modelo e gera uma curva de
calibração comparando os 3.

**Uso:** `python -m src.models.tune_models`
**Lê:** `data/features.csv`.
**Escreve:** stdout (métricas + melhores parâmetros) e
`reports/calibration_curve.png`.

### `src/models/export_model.py`
Treina um XGBoost (hiperparâmetros tunados de `tune_models.py` —
retunados no dataset de 10k em 2026-07-03: lr 0.01, max_depth 3,
`n_estimators` 500) POR CORTE de tempo (10/15/20/25 min) e exporta os
modelos de produção para o endpoint `/predict` e para a análise de
partida, junto com a importância SHAP por fase para o front end.

**Uso:** `python -m src.models.export_model`
**Lê:** `data/features_phases.csv`.
**Escreve:** `data/models_phases.joblib` ({corte: modelo}, carregado
pela API no startup), `data/model.joblib` (corte de 15, compat.),
`reports/shap_importance_phases.json` e `reports/shap_importance.json`.
**Observação:** rodar de novo sempre que as features forem regeneradas.

### `src/models/explain_shap.py`
Treina um XGBoost (hiperparâmetros vindos do `tune_models.py`) e gera
gráficos SHAP (importância global em barras + beeswarm) para o capítulo
de explicabilidade.

**Uso:** `python -m src.models.explain_shap`
**Lê:** `data/features.csv`.
**Escreve:** `reports/shap_importance.png`, `reports/shap_beeswarm.png`.

---

## Interface em linguagem natural (`src/nlq/`)

### `src/nlq/schema_context.py`
Não é executável — define `SCHEMA_DESCRIPTION`, o texto de sistema
(schema das tabelas + regras de formatação de SQL) enviado ao LLM em
todo pedido de geração de SQL. Alterar aqui muda o comportamento de
`nl_to_sql.py` e `evaluate_nlq.py` — **sempre rode `python -m
src.nlq.evaluate_nlq` de novo depois de qualquer mudança aqui** (já
regrediu silenciosamente de 95% para 77% uma vez por causa disso).
Inclui, além do schema, regras aprendidas de bugs reais encontrados
testando perguntas (todas com exemplo de SQL correto e copiável — um
exemplo rotulado "errado" ao lado do certo se mostrou arriscado, o
modelo pode imitar a estrutura errada mesmo rotulada como tal):
join seguro entre `bans` e `participants` (nunca direto por
champion_id — explosão cartesiana e timeout; usar subquery deduplicada
por `SELECT DISTINCT`), e cálculo de taxa de um subgrupo (ex.: só o
time vermelho) quando o `GROUP BY` não isola esse subgrupo (nunca
`CASE WHEN ... THEN 1 ELSE 0` dentro de um `AVG` rodando sobre linhas
de fora do subgrupo — dilui a taxa, chega a sair pela metade do valor
real; sempre `WHERE` para isolar antes de agregar, ou `GROUP BY`
também pela coluna do subgrupo se a pergunta quiser os dois lados).

### `src/nlq/nl_to_sql.py`
Text-to-SQL: envia a pergunta + `SCHEMA_DESCRIPTION` para o Claude
(`claude-haiku-4-5`, `temperature=0` para determinismo), valida a query
gerada (só `SELECT`, sem múltiplos statements, sem palavras-chave de
escrita, só tabelas do schema) e executa com `statement_timeout=10s`.

**Uso:** `python -m src.nlq.nl_to_sql "qual campeão tem maior win rate?"`
**Requer:** `ANTHROPIC_API_KEY` no `.env`.
**Lê:** banco (tabelas `matches`/`teams`/`participants`/`players`);
Claude API.
**Escreve:** stdout (SQL gerada + resultado).

### `src/nlq/nl_to_sql.py` — diagnóstico de erros e conversas
`generate_sql()` aceita um `history` opcional (turnos anteriores
`{question, sql}`, enviados como mensagens user/assistant alternadas ao
Claude) para dar contexto a perguntas de acompanhamento. Se a SQL for
cortada por `max_tokens` (perguntas com muitas condições), levanta
`ValueError` claro em vez de deixar a SQL truncada estourar como erro de
sintaxe. `ask()` propaga falhas de execução como `SqlExecutionError`
(carrega `sql` + `cause`, a exceção original do psycopg2) em vez de uma
mensagem genérica — o endpoint `/ask` usa isso para devolver a SQL
gerada e o erro real do banco, não só "tente reformular".

### `src/nlq/nl_to_sql.py` — `explain_result()`
Além de `generate_sql`/`ask`, o módulo tem `explain_result(question, sql,
columns, rows)`: gera uma explicação em linguagem natural (português,
sem markdown, sem jargão de SQL) do resultado de uma consulta, usada
pelo endpoint `POST /ask/explain`. Chamada em endpoint separado (não
junto com `ask()`) para não dobrar custo de API quando só a SQL/tabela
interessa; o front (`Nlq.tsx`) dispara essa chamada automaticamente ao
receber cada resposta, já que "Explicação" é a aba padrão do toggle
"SQL / Explicação" (trocado de padrão em 2026-07-03 — antes só buscava
sob demanda, no clique). O prompt inclui um parágrafo curto de
"convenções do banco" (team_id 100=azul/200=vermelho, win rate já é
fração 0-1, stats de participants/duração são totais finais) — sem
isso, o modelo tem que adivinhar o significado de colunas como
`team_id` e pode inverter lado (bug real encontrado e corrigido em
2026-07-03: a explicação atribuía os números do time 100 ao "vermelho"
e do 200 ao "azul", exatamente trocado). A explicação também: (a)
avalia a confiança estatística e avisa quando algum grupo tem menos de
~30 partidas (win rates de amostras pequenas variam dezenas de pp só
por acaso); (b) quando relevante, acrescenta um trecho iniciado por
"Leitura de jogo:" com conhecimento de LoL que os números não capturam,
explicitamente rotulado como conhecimento do jogo (não dos dados) e
apontando se concorda ou discorda dos números.

### `src/nlq/evaluate_nlq.py`
Validação metodológica da interface NL exigida pela banca: 22 perguntas
de referência com SQL "gold", comparando o RESULTADO (não o texto) da
query gerada com o da query de referência. Métrica: execution accuracy.

**Uso:** `python -m src.nlq.evaluate_nlq`
**Requer:** `ANTHROPIC_API_KEY`.
**Lê:** banco; Claude API.
**Escreve:** stdout (OK/FALHA por pergunta + accuracy final).

---

## API e Dashboard

### `src/api/main.py`
API FastAPI que alimenta o front end React (e qualquer outro cliente):
- `GET /stats/overview` — contagens gerais + patches cobertos + win rate
  do lado azul;
- `GET /stats/champions` — estatísticas completas por campeão (win/pick/
  ban rate, KDA, CS, ouro, dano, posição principal), com params
  `min_games`, `limit`, `sort` (whitelist), `role` (posição) e `search`;
- `GET /stats/champion/{nome}` — detalhe de um campeão: stats gerais,
  por posição, matchups na mesma lane (>= 15 jogos) e últimas partidas;
- `GET /stats/champion/{nome}/items` — itens finalizados mais
  construídos pelo campeão (>= 20 jogos com o item): jogos, % dos jogos
  do campeão, win rate e minuto médio da PRIMEIRA compra do item na
  partida (recompra após venda não conta como jogo novo). Lê
  `item_events` + o catálogo `data/items.json` (503 se o catálogo não
  existir);
- `GET /stats/objectives` — média de objetivos por resultado;
- `GET /stats/durations` — histograma de duração das partidas (5 min);
- `GET /stats/gold15` — win rate azul por faixa de diferença de ouro aos
  15 min (lido de `data/features.csv`, cache invalidado por mtime);
- `GET /matches/recent` — últimas partidas com os 10 participantes;
- `GET /matches/{id}/analysis` — análise completa de uma partida: curva
  de probabilidade de vitória minuto a minuto (roda o modelo da fase
  correspondente sobre o estado real de cada minuto da timeline), curva
  de ouro, stats por jogador e objetivos. Cada ponto da curva carrega o
  ESTADO completo do minuto (os 5 diffs) — semente do modo "e se" no
  front (card em `/partidas/:id` que edita o estado real e mostra o
  delta de probabilidade via `/predict`);
- `GET /stats/highlights` — destaques para a página inicial (melhor
  jogador, melhor campeão, matchup mais desequilibrado, mais banido,
  viés de lado), com os números que fundamentam cada insight;
- `GET /stats/patches` — partidas e win rate azul por patch (cobertura
  do dataset);
- `GET /matches/{id}/positions` — posições x/y dos 10 jogadores minuto a
  minuto (participantFrames da timeline, com nível) + abates com local +
  eventos de objetivo (torre/dragão/barão/arauto/inibidor com minuto e
  time; em BUILDING_KILL o `teamId` do evento é o DONO da construção,
  então pontua o oposto) — base do mapa de calor e do card de objetivos
  por minuto; 404 se a partida não tem timeline;
- `POST /compose` — análise de composição (montar time): matchups por
  lane (confronto direto >= 10 jogos, senão aproximação por perfil),
  sinergias de dupla (>= 20 jogos, delta vs média individual) e
  estimativa heurística agregada — explicitamente distinta do modelo ML.
  Valida que nenhum campeão se repete na partida (regra do jogo). Aceita
  `state` opcional (mesmo shape do `/predict`): devolve `state_analysis`
  com a probabilidade do modelo ML naquele minuto, a taxa-base (tudo
  zerado) e a estimativa combinada em log-odds
  (`logit(combinado) = logit(ML) + logit(composição)` — o termo ML já
  carrega a taxa-base/viés de lado; a composição entra como evidência
  extra centrada em 50%);
- `GET /stats/pro/overview`, `/stats/pro/gold15`, `/stats/pro/champions`
  — dataset competitivo (pro_games/pro_players, Oracle's Elixir) para a
  página `/competitivo`: visão geral + ligas, win rate azul por faixa de
  ouro aos 15 min (mesmas faixas do /stats/gold15 para comparação
  direta) e campeões do meta pro com o win rate de solo queue ao lado
  (match de nomes normalizado; Wukong/Renata/Nunu têm CASE especial);
- `POST /ask` — pergunta em linguagem natural via `nl_to_sql.ask`
  (OBS: as tabelas pro_* ainda NÃO estão no schema_context do NLQ);
- `POST /predict` — probabilidade de vitória do time azul a partir do
  estado da partida + contribuições SHAP; aceita `minute` (10|15|20|25)
  para escolher o modelo da fase (exige `data/models_phases.joblib`, ver
  `export_model.py`; sem ele retorna 503);
- `/reports/*` — serve os PNGs/JSON de `reports/` (explicabilidade).

CORS liberado para `http://localhost:5173` (dev server do Vite).

**Uso:** `uvicorn src.api.main:app --reload`
**Lê:** banco; Claude API (endpoint `/ask`); `data/model.joblib`.

### `frontend/` (aplicação React)
Interface principal da plataforma: Vite + React + TypeScript, Tailwind
CSS v4, Recharts (gráficos), TanStack Query (dados), React Router.
Páginas: Início (herói hextech com splash art + busca de campeão
estilo op.gg, faixa de números do dataset, rankings top-5 com
micro-barras — maior win rate/mais jogados/mais banidos —, insights com
"porquê" e feed de partidas recentes), Dashboard analítico
(`/dashboard`, organizado em 3 seções narrativas — o que decide
partidas / retrato do meta / cobertura do dataset — cada gráfico com
uma linha "Leitura:" calculada dos próprios dados), Campeões (tabela
estilo op.gg + detalhe com matchups em `/campeoes/:nome`), Partidas
(feed em `/partidas` + análise completa em `/partidas/:id` com curva de
probabilidade, mapa de calor com slider de minuto — componente
`MapHeatmap`, canvas + ícones + abates sobre o esquema OFICIAL de
Summoner's Rift (`MINIMAP_URL` em `ddragon.ts`,
`raw.communitydragon.org/.../maps/info/map11/2dlevelminimap_base_baron1.png`
— mesmo estilo esquemático que a Riot usa em posts oficiais de mudança
de mapa, mas servido a partir do patch `latest` de verdade — o
`map11.png` do Data Dragon trava numa versão congelada, confirmado
testando 6.8 a 16.13; achado via busca no índice
`cdragon/files.exported.txt` depois que uma textura realista
(`grasstint.png`) e depois um SVG próprio desenhado à mão se mostraram
etapas intermediárias — ver diário de 2026-07-03. PNG com transparência
real na selva, composto sobre a cor de fundo do próprio container) — e
objetivos em barras espelhadas SINCRONIZADOS com o minuto do slider,
com fallback para os totais finais quando não há timeline), Consulta
NL, Predição
(seletor de fase 10/15/20/25 min), Montar Partida (`/montar` — team
builder 5v5 com busca de campeão por nome (`ChampionCombobox`: digita e
filtra, navegação por teclado, botão de limpar — não é mais um
`<select>` nativo), sem campeões repetidos, com matchups por lane,
sinergias, e estado da partida opcional que combina a composição com o
modelo ML) e
Explicabilidade (importância SHAP por fase em barras + gráfico de
evolução da importância ao longo das fases, uma linha por fator) —
todas consumindo a API FastAPI (nunca o banco diretamente).
Identidade visual hextech unificada: componente `PageHeader` (rótulo
dourado + título serifado + linha de brilho) em todas as páginas;
ranges/fases dos sliders de estado compartilhados em
`src/lib/matchState.ts` (usados por Predição e Montar Partida).
Tema dark/light com toggle persistido em `localStorage`. Ícones de
campeão via CDN CommunityDragon (por `champion_id`, helper em
`src/lib/ddragon.ts`).

**Uso:** `cd frontend && npm install && npm run dev`
(requer a API rodando em `http://localhost:8000`; a URL é configurável
em `frontend/.env` via `VITE_API_URL`).

### `src/dashboard/app.py`
Dashboard Streamlit: KPIs gerais, gráficos de campeões (win rate e mais
jogados), objetivos×vitória, e caixa de pergunta em linguagem natural.
Consulta o banco diretamente (não passa pela API FastAPI).

**Uso:** `streamlit run src/dashboard/app.py`
**Lê:** banco; Claude API (seção de pergunta NL).
**Observação:** diferente dos outros scripts (todos rodados via
`python -m`), este é o único ponto de entrada que não usa `-m` — por
isso o arquivo insere manualmente a raiz do projeto em `sys.path` no
topo (ver comentário no código), senão o import `from src...` falha
com `ModuleNotFoundError`.

---

## Testes

### `tests/smoke_test.py`
Teste de fumaça sem banco e sem API: gera partidas sintéticas (timeline
fake com vantagem de ouro correlacionada à vitória), roda
`features_from_timeline` e `train_baseline` nelas. Serve para validar
que o ambiente Python está funcional antes de configurar banco/chaves.

**Uso:** `python tests/smoke_test.py`
**Lê/escreve:** nada externo — tudo sintético, escrito em um diretório
temporário. (Até a revisão de 2026-07-03 sobrescrevia o
`data/features.csv` REAL com os 400 sintéticos — e como o
`/stats/gold15` da API lê esse arquivo com cache por mtime, o dashboard
passaria a exibir dados falsos. Corrigido: o teste roda com `chdir` em
um `TemporaryDirectory`.)

### `tests/validate_predictions.py`
Bateria de validação COMPORTAMENTAL do modelo de produção (diferente
das métricas de teste de `train_baseline.py`/`tune_models.py`, que
medem acerto médio — este script testa se o modelo se comporta como
esperado): monotonicidade por fator (mais vantagem não deveria reduzir
a prob. do azul), casos extremos (liderança/déficit total, simetria),
taxa-base por fase (viés de lado com tudo empatado), evolução da
importância SHAP entre fases, e uma checagem retrospectiva rodando o
pipeline completo (timeline real → features → modelo por fase) em uma
amostra de partidas reais, comparando a direção da predição nos
últimos minutos com o vencedor de fato. Resultado de 2026-07-03: os
únicos "FALHA" são monotonicidade isolada de `kill_diff`/`tower_diff`
(esperado — baixa importância/redundância já documentada no SHAP,
testar um fator isolado com os outros 4 em zero é um estado artificial
fora da distribuição de treino) e a taxa-base aos 25min ligeiramente
> 50% (esperado — "empatado aos 25min" é uma população condicional
diferente do viés de lado incondicional de 56,3%). Ver a entrada do
diário do mesmo dia para a interpretação completa.

**Uso:** `python tests/validate_predictions.py`
**Lê:** `data/models_phases.joblib`, `data/features_phases.csv`, banco
(amostra de `raw_timelines` para a checagem retrospectiva).
