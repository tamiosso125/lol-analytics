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
Busca os ladders Challenger/Grandmaster/Master (fila 420) na Riot API e
faz upsert na tabela `players` (puuid, tier, liga, pontos, platform).
Multi-região (sprint 5 do planejamento v2): `--platforms` aceita várias
plataformas na mesma chamada, cada uma com seu próprio `RiotClient`
(rate limit por instância).

**Uso:** `python -m src.collect.seed_players`
(padrão: só a plataforma do `.env`) ou
`python -m src.collect.seed_players --platforms br1 kr euw1 na1 --tiers CHALLENGER GRANDMASTER MASTER`
**Lê:** Riot API (`challengerleagues`/`grandmasterleagues`/`masterleagues`).
**Escreve:** tabela `players`.

### `src/collect/backfill_names.py`
Preenche `game_name`/`tag_line` dos jogadores via account-v1 (o endpoint
de liga não retorna mais nomes, só puuid). Uma requisição por jogador,
respeitando o rate limit; processa só quem ainda está sem nome.

**Uso:** `python -m src.collect.backfill_names --min-games 20`
**Lê:** tabelas `players`/`participants`; Riot API (account-v1).
**Escreve:** colunas `game_name`/`tag_line` de `players`.

### `src/collect/collect_matches.py`
Para os N jogadores com mais LP em `players` (por plataforma), busca os
últimos match_ids (fila 420) e baixa match + timeline de cada um que
ainda não está no banco. JSON bruto vai para `raw_matches`/
`raw_timelines`; cada partida é normalizada na hora via `load_one`
(ETL). Multi-região (sprint 5): agrupa os jogadores selecionados por
`platform` e usa um `RiotClient` roteado pra região certa por grupo,
sequencial entre plataformas (nunca paralelo — mesmo quando duas
plataformas roteiam pra mesma região, ex. br1+na1→americas).

**Uso:** `python -m src.collect.collect_matches --players 730 --matches-per-player 40`
(todas as plataformas em `players`) ou
`python -m src.collect.collect_matches --platforms kr euw1 na1 --players 20 --matches-per-player 8`
(flags: `--platforms` filtra plataformas, `--players` N por plataforma,
`--matches-per-player` quantos match_ids recentes buscar por jogador,
`--no-timeline` para pular o download da timeline).
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
Extrai as compras/vendas/consumos de itens dos eventos ITEM_* das
timelines para a tabela `item_events` (~10,4M linhas em 23k partidas).
Os `ITEM_UNDO` são aplicados no ETL (a compra desfeita não entra — a
tabela reflete o que o jogador manteve, não cada clique na loja). Só
processa timelines cuja partida existe em `matches` (raw_timelines tem
remakes que o ETL principal pula — sem o filtro, viola a FK). A tabela
é reconstruída do zero a cada execução (TRUNCATE) — rodar após
qualquer coleta nova. O catálogo `data/items.json` (nome, custo, tags,
receitas por item_id) vem do Data Dragon
(`cdn/16.13.1/data/pt_BR/item.json`, versão fixada em sincronia com o
helper `itemIcon` do front) — a API o carrega no startup e deriva duas
listas: `_completed_item_ids` ("itens finalizados" — nada constrói a
partir dele, comprável, custo >= 1100, não consumível/trinket, válido
no mapa 11 — usada em `champion_items`/coach) e `_trackable_item_ids`
(2026-07-08, mesma coisa SEM exigir "finalizado" — inclui botas e
componentes, usada só no build por minuto de `/matches/{id}/positions`).

**`ITEM_DESTROYED` é gravado desde 2026-07-08** (ação `DESTROY`,
`action` virou `VARCHAR(10)` — cabia só `VARCHAR(4)` antes, migração
aplicada). Antes era ignorado de propósito ("interessa o que foi
comprado, não a fusão de componentes") — mas sem isso, reconstruir "o
que o jogador tinha no inventário no minuto X" deixava componentes
fantasmas pra sempre depois de virarem item final. Confirmado seguro:
todo consumidor de `item_events` já trata qualquer ação != BUY como
remoção, então adicionar DESTROY não quebra nada que já lia a tabela.
Limite conhecido: ITEM_UNDO só desfaz BUY/SELL (a Riot nunca
referencia um DESTROY em beforeId/afterId) — desfazer a compra que
finaliza uma receita deixa os componentes permanentemente "destruídos"
na reconstrução, caso raro não tratado.

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

### `src/models/train_pro.py`
Comparação formal solo queue × competitivo (sprint 2 do planejamento
v2): o mesmo XGBoost tunado de produção, avaliado por CV 5-fold, sobre
as features COMPARTILHADAS aos 15 min (gold/xp/kill diff — existem nos
dois datasets) e sobre o conjunto completo de cada um. Também treina e
salva `data/model_pro.joblib` (3 features compartilhadas, todos os anos
do pro) — insumo do futuro "pro ao vivo" (o feed de livestats fornece
exatamente ouro/XP/abates). Resultado de 2026-07-05: AUC praticamente
idêntica (solo 0,8255 × pro 0,8283 nas mesmas features) — o pro
converte vantagens grandes melhor, mas chega menos vezes a vantagens
extremas (desvio do gold_diff aos 15: 2.991 pro × 4.199 solo), e os
efeitos se cancelam no agregado. Ver diário do mesmo dia.

**Uso:** `python -m src.models.train_pro`
**Lê:** `pro_games` (banco), `data/features.csv`.
**Escreve:** `data/model_pro.joblib`, stdout (tabela comparativa).

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
Validação metodológica da interface NL exigida pela banca: 26 perguntas
de referência com SQL "gold" (22 de solo queue + 4 do competitivo,
incluindo o join duplo pro_players↔pro_games), comparando o RESULTADO
(não o texto) da query gerada com o da query de referência. Métrica:
execution accuracy — faixa medida: 85-95% (as falhas flutuantes são
todas a família benigna "coluna COUNT extra em perguntas com limiar de
jogos", documentada no diário).

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
- `GET /stats/champion/{nome}/pro` — presença/win rate do campeão no
  COMPETITIVO (jogos, presença sobre o ano, quebra por liga; `?year=`
  padrão mais recente; match de nome interno↔exibição igual ao
  /stats/pro/champions);
- `GET /stats/champion/{nome}/items` — itens finalizados mais
  construídos pelo campeão (>= 20 jogos com o item): jogos, % dos jogos
  do campeão, win rate e minuto médio da PRIMEIRA compra do item na
  partida (recompra após venda não conta como jogo novo). Lê
  `item_events` + o catálogo `data/items.json` (503 se o catálogo não
  existir). Query extraída em `_champion_top_items(cur, champion_name,
  min_games, limit)` (2026-07-08) — reutilizada pelo `/coach` (ver
  abaixo) pra grounded a sugestão de build em dado real;
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
  delta de probabilidade via `/predict`). Cada participante também
  carrega `items` (2026-07-06: 7 slots finais — item6 é o trinket — lidos
  de `raw_matches.payload.info.participants[].item0..item6`, que a Riot
  já grava pronto; não precisa reconstruir do `item_events`, que é pra
  ORDEM de compra, não pro estado final);
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
  por minuto; 404 se a partida não tem timeline. Também retorna `wards`
  (2026-07-06: `WARD_PLACED`/`WARD_KILL`) — a Riot NÃO grava a posição da
  ward no evento, só quem/quando, então usa a posição do jogador que
  agiu naquele minuto como proxy aproximado (filtra `wardType ==
  UNDEFINED`, artefato do início da partida, e `creatorId`/`killerId ==
  0`, evento de sistema); o front precisa deixar a aproximação
  explícita (`MapHeatmap`, toggle "Wards (aproximado)", desligado por
  padrão, e o card "Controle de visão" que só usa contagem, sem
  posição). Cada jogador de cada frame também carrega `items`
  (2026-07-08) — itens finalizados que ele possuía NAQUELE minuto,
  reconstruído andando pelos `item_events` em paralelo com os frames
  (uma query ordenada por ts_ms, não uma por minuto); usado pela coluna
  "Itens" da `TeamTable` no `MatchDetail`, que agora acompanha o slider
  do mapa de calor em vez de mostrar só o build final. Não rastreia
  trinket (fora do filtro de itens "finalizados"). **Ganhou
  `gold`/`cs`/`dmg`/`kills`/`deaths`/`assists` por minuto também
  (2026-07-08, bug reportado — só itens tinham sido corrigidos, o
  resto ainda mostrava totais finais)**: `gold`/`cs`/`dmg` vêm direto
  do `participantFrame` (`totalGold`, `minionsKilled`+
  `jungleMinionsKilled`, `damageStats.totalDamageDoneToChampions`);
  `kills`/`deaths`/`assists` reconstroem contando eventos
  `CHAMPION_KILL` até o minuto (mesma técnica de dois ponteiros dos
  itens, lista pré-ordenada por timestamp). **NÃO inclui visão**
  (`visionScore`) — a Riot só grava o total final da partida, nenhuma
  versão da match-v5 grava incrementalmente; a `TeamTable` mostra isso
  sempre fixo no total final, com nota explícita na UI;
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
  extra centrada em 50%). Aceita `blue_players`/`red_players` opcionais
  (posição→puuid): ajusta cada lane pelo desempenho do jogador NAQUELE
  campeão com shrinkage bayesiano (`k=15` jogos equivalentes de prior —
  `shrunk = (jogos*wr_jogador + k*wr_campeão) / (jogos+k)`, aplicado em
  log-odds sobre a lane); a resposta de cada lane traz
  `composition_win_rate` (sem jogador) e `blue_player`/`red_player`
  (nome, jogos, wr bruto e após shrinkage) para a UI mostrar o cálculo,
  não só o resultado;
- `GET /stats/regions` — cobertura e viés de lado (win rate do
  vermelho) por `platform_id` — a mesma pergunta do viés de lado BR,
  agora comparável entre plataformas (sprint 5 do planejamento v2);
- `GET /matches/random` — um match_id aleatório com timeline e >= 20
  min — semente do replay "ao vivo" (`/aovivo`, sprint 6);
- `GET /stats/players/search?q=` — busca de jogadores nos DOIS datasets
  (solo queue por game_name/Riot ID; competitivo por player_name) para
  a busca unificada da Home (mínimo 3 caracteres);
- `GET /stats/player/{puuid}` — perfil de jogador de solo queue:
  identidade/tier, totais, pool de campeões, últimas partidas;
- `GET /stats/pro/player/{nome}` — perfil de jogador profissional:
  temporadas (ano/time/liga), pool de campeões da carreira (ícones via
  match de nomes), totais; nome casado case-insensitive;
- `GET /stats/pro/overview`, `/stats/pro/gold15`, `/stats/pro/champions`,
  `/stats/pro/years` — dataset competitivo (pro_games/pro_players,
  Oracle's Elixir, 13 anos/99k jogos) para a página `/competitivo`:
  visão geral + ligas, win rate azul por faixa de ouro aos 15 min
  (mesmas faixas do /stats/gold15 para comparação direta), campeões do
  meta pro com o win rate de solo queue ao lado (match de nomes
  normalizado; Wukong/Renata/Nunu têm CASE especial) e anos
  disponíveis. Todos aceitam `?year=` (padrão: ano mais recente — sem o
  filtro, as análises misturariam metas de eras diferentes);
- `POST /ask` — pergunta em linguagem natural via `nl_to_sql.ask`
  (OBS: as tabelas pro_* ainda NÃO estão no schema_context do NLQ);
- `POST /predict` — probabilidade de vitória do time azul a partir do
  estado da partida + contribuições SHAP; aceita `minute` (10|15|20|25)
  para escolher o modelo da fase (exige `data/models_phases.joblib`, ver
  `export_model.py`; sem ele retorna 503);
- `POST /coach` (2026-07-08, `src/coach/advice.py`) — orientação
  estratégica em texto a partir do `state`+`blue_win_probability`+
  `shap_contributions` que o `/predict` já calculou (não recalcula
  nada). Camada 1 do plano "conhecimento geral aplicado à predição" —
  usa o conhecimento geral de League of Legends da LLM pra traduzir os
  números em "o que fazer agora", sempre terminando com aviso de que
  não é verificado pelos dados da partida (modelo não vê itens/posição/
  wave). **Camada 2** (mesma data): campos opcionais
  `blue_champions`/`red_champions` (por posição), `lanes` e
  `blue_synergies`/`red_synergies` — os mesmos números que o
  `/compose` já calcula (shrinkage+IC), nunca invenção da LLM; o
  prompt distingue "dado real" de "conhecimento geral" e só cita
  estatística fornecida. **Camada 2 (itens/posição) + Camada 3** (mesma
  data, estendida em seguida): com `match_id`+`game_minute` opcionais,
  o servidor chama `src/coach/tactics.py` (`tactical_context`) e
  injeta DADO REAL da timeline no minuto — itens finalizados que cada
  campeão já possuía + sinais espaciais derivados (agrupamento dos 5,
  overextensão além do rio, tempo de selva) + **visão e momentum**
  (wards de controle/normais e abates numa janela de 4 min — contagem
  EXATA de evento, não aproximação como a posição). O aviso do prompt
  vira condicional (itens/posição/visão/momentum reais mas posição
  aproximada a 1 amostra/min; wave/minion não observável — essa é a
  única fatia da Camada 3 que segue bloqueada, exige replay .rofl ou
  visão computacional). Consumido pelo `CoachCard` (frontend): card "E
  se..." do `MatchDetail` passa match_id → contexto tático completo;
  aba Composição do Simulador é composição hipotética → só campeões/
  matchups/sinergias, sem match_id. **Build sugerida estruturada**
  (2026-07-08, com correção de precisão + confiabilidade no mesmo dia):
  `generate_advice()` faz DUAS chamadas de LLM — a primeira escreve só
  a `narrative` (texto livre, sem tool calling); a segunda
  (`_extract_build_suggestions`, temperatura 0.2, tool
  `EXTRACT_BUILDS_TOOL`) relê esse texto já escrito e extrai as
  menções de item — uma tarefa de releitura mecânica, não uma decisão
  concorrendo com a escrita da narrativa. `/coach` resolve nome →
  `item_id` real via `_item_name_to_id` (descarta a sugestão se o nome
  não bater com item nenhum do catálogo). Antes era uma chamada só
  (tool calling forçado com `narrative`+`build_suggestions` no mesmo
  schema) — funcionava, mas a taxa de acerto da parte estruturada
  desabava toda vez que o prompt crescia (mesma diluição de atenção do
  `schema_context.py` do NLQ); separar em duas chamadas focadas subiu
  de ~0/3-2/6 pra 6/6 em teste.
  **Itens grounded em dado real**: `/coach` busca, pra cada campeão
  conhecido, os itens finalizados mais construídos com win rate real
  via `_champion_top_items()` (mesmo helper do
  `/stats/champion/{name}/items`, `limit=3`) e passa como `top_items`
  pro prompt — a LLM prefere sugerir DESSA lista em vez de recordar de
  memória (achado real: sugeriu "Coração de Aço" pra Camille com
  motivo "resistência mágica" quando o item só dá Vida/Regen — sem
  grounding, a explicação do PORQUÊ pode estar errada mesmo quando o
  item escolhido existe de verdade). Renderizado como seção "Build
  sugerida" no `CoachCard`, ícones reais via `itemIcon()`.
- `POST /coach/draft` (2026-07-08, `generate_draft_analysis` em
  `src/coach/advice.py`) — leitura de DRAFT: win condition, contra-pick
  e quem escala melhor, usando só os 10 campeões (sem `MatchState`, sem
  probabilidade do modelo — pergunta estruturalmente diferente do
  `/coach`, "quem tem vantagem pelo draft" em vez de "quem está
  ganhando agora"). `lanes`/`blue_synergies`/`red_synergies` opcionais
  (mesmos dados reais do `/compose`, quando disponíveis). Consumido
  pelo `DraftAnalysisCard` (frontend): aparece no topo do `MatchDetail`
  (antes da curva de probabilidade, só campeões da partida real — não
  chama `/compose`, fica registrado como possível melhoria futura) e na
  aba Composição do Simulador (contexto completo, `result.lanes`+
  `result.synergies` já calculados — ao contrário do `CoachCard`,
  aparece MESMO sem "Estado da partida" marcado).
- `/reports/*` — serve os PNGs/JSON de `reports/` (explicabilidade).

CORS liberado para `http://localhost:5173` (dev server do Vite).

**Uso:** `uvicorn src.api.main:app --reload`
**Lê:** banco; Claude API (endpoint `/ask`); `data/model.joblib`.

### `frontend/` (aplicação React)
Interface principal da plataforma: Vite + React + TypeScript, Tailwind
CSS v4, Recharts (gráficos), TanStack Query (dados), React Router.

**Navegação consolidada em 2026-07-06** (10 → 6 itens na sidebar — ver
diário da data para o brainstorm/justificativa completa): Início,
Dashboard, Campeões, Competitivo, Consulta NL, Simulador. As páginas
"Partidas", "Predição", "Ao vivo", "Explicabilidade" e "Montar partida"
não existem mais como itens de nav — absorvidas nas páginas abaixo.
Rotas antigas redirecionam (`App.tsx`: `/partidas`→`/`,
`/predicao`/`/explicabilidade`/`/montar`→`/simulador`,
`/aovivo`→`/`, qualquer rota desconhecida→`/`).

Páginas:
- **Início** (`/`): herói hextech com splash art + busca de campeão
  estilo op.gg, faixa de números do dataset, rankings top-5 com
  micro-barras (maior win rate/mais jogados/mais banidos), insights com
  "porquê", e feed de 8 partidas recentes com botão **"assistir ao
  vivo"** (sorteia uma partida via `/matches/random` e navega para
  `/partidas/:id?replay=1` — absorve a antiga página "Partidas" que
  era só esse feed sem nenhum filtro/busca próprio).
- **Dashboard** (`/dashboard`): 3 seções narrativas — o que decide
  partidas / retrato do meta / cobertura do dataset — cada gráfico com
  uma linha "Leitura:" calculada dos próprios dados.
- **Campeões** (`/campeoes` + detalhe `/campeoes/:nome`): tabela estilo
  op.gg + matchups.
- **Partida** (`/partidas/:id`): curva de probabilidade minuto a
  minuto, mapa de calor com slider (`MapHeatmap`, canvas + ícones +
  abates sobre o esquema OFICIAL de Summoner's Rift — `MINIMAP_URL` em
  `ddragon.ts`,
  `raw.communitydragon.org/.../maps/info/map11/2dlevelminimap_base_baron1.png`,
  servido do patch `latest` de verdade, ao contrário do `map11.png`
  congelado do Data Dragon — achado via `cdragon/files.exported.txt`,
  ver diário de 2026-07-03), objetivos em barras espelhadas
  sincronizadas com o minuto, e o card "E se…" de contrafactual de
  estado. **Ganhou modo replay em 2026-07-06** (`ProbabilityCard` em
  `MatchDetail.tsx`, absorve a antiga página "Ao vivo"): botão
  "Assistir como replay" anima a MESMA curva já carregada minuto a
  minuto (play/pausa/velocidade/reiniciar, revela o resultado real ao
  fim, botão "Outra partida" sorteia outra) — `?replay=1` na URL
  autoplaya direto (é pra onde o botão da Início navega). Sem fetch
  duplicado: a página estática e o replay usam o mesmo `prob_curve` já
  buscado. **Estilo broadcast em 2026-07-08**: `ProbabilityCard` ganhou
  prop `onMinuteChange`, disparada a cada tick do replay — como o mapa
  de calor/itens/objetivos já eram reativos ao MESMO `minute` do
  `MatchDetail` (antes só controlado pelo slider), passaram a
  acompanhar o replay automaticamente, sem mudar esses três
  componentes. O card "E se..." também acompanha de graça (mesmo
  `minute`).
- **Consulta NL** (`/consulta`).
- **Simulador** (`/simulador`, `Simulador.tsx`): **fusão de 3 páginas
  em 2026-07-06** (Montar Partida + Predição + Explicabilidade — todas
  usavam o mesmo modelo/estado `src/lib/matchState.ts` para a mesma
  audiência). 3 abas internas, cada uma um "painel" sem `PageHeader`
  próprio (o Simulador supre um só):
  - **Composição** (`CompositionPanel`, em `TeamBuilder.tsx`): team
    builder 5v5, busca de campeão por nome (`ChampionCombobox`: digita
    e filtra, navegação por teclado — não é `<select>` nativo), sem
    campeões repetidos, matchups por lane, sinergias, jogadores
    opcionais com shrinkage, estado da partida opcional combinado ao
    modelo ML.
  - **Estado** (`StatePanel`, em `Predict.tsx`): sliders de estado
    (ouro/xp/abates/torres/dragões) por fase 10/15/20/25 min →
    probabilidade + contribuição SHAP da predição — mesmos
    componentes/ranges da aba Composição, mas sem precisar escolher
    campeão nenhum.
  - **Explicabilidade** (`ExplainPanel`, em `Explain.tsx`): importância
    SHAP média por fase (barras) + evolução ao longo das fases (linha,
    uma por fator) + beeswarm + curva de calibração.
- **Competitivo** (`/competitivo` — solo queue × pro, seletor de ano) e
  perfis de jogador (`/jogadores/:puuid` solo queue,
  `/competitivo/jogadores/:nome` pro).

Todas consumindo a API FastAPI (nunca o banco diretamente). Identidade
visual hextech unificada: componente `PageHeader` (rótulo dourado +
título serifado + linha de brilho) em toda página de topo (não nos
painéis do Simulador — só a página-mãe tem um). Tema dark/light com
toggle persistido em `localStorage`. Ícones de campeão via CDN
CommunityDragon (por `champion_id`, helper em `src/lib/ddragon.ts`).

**Uso:** `cd frontend && npm install && npm run dev`
(requer a API rodando em `http://localhost:8000`; a URL é configurável
em `frontend/.env` via `VITE_API_URL`).

**Qualidade (2026-07-06):** `npm run lint` (ESLint flat config —
`typescript-eslint` + `eslint-plugin-react-hooks` + `react-refresh`,
pegou 5 bugs reais na primeira rodada: componente recriado a cada
render em `Home.tsx`, `setState` síncrono dentro de efeito em
`MatchDetail.tsx`/`Nlq.tsx` — todos corrigidos), `npm run test`
(Vitest + Testing Library — 19 testes unitários de `lib/format.ts` e
`lib/ddragon.ts`, 14 smoke tests que renderizam cada página sob os
providers reais com `api` mockado via `vi.mock` + `Proxy`, ver
`src/pages/pages.smoke.test.tsx`), `npm run build` (inclui `tsc`).
`ErrorBoundary` (`src/components/ErrorBoundary.tsx`) envolve o
`<Outlet />` no `Layout.tsx`, `key`ado pela rota — página que quebra em
render mostra fallback em vez de tela branca, e navegar para outra
página a desmonta.

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
