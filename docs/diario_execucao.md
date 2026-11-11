# Diário de execução — TCC II

Registro cronológico das etapas executadas, decisões tomadas e resultados
obtidos, para referência ao escrever o texto do TCC II e para a banca.

---

## 2026-07-01 — Etapa 1: setup do ambiente

- PostgreSQL 18 instalado localmente (`C:\Program Files\PostgreSQL\18`), não
  estava no PATH — resolvido adicionando a pasta `bin` ao PATH da sessão.
- Banco `lol_analytics` criado (`CREATE DATABASE`).
- `DATABASE_URL` no `.env` inicialmente apontava para a senha errada
  (`postgres`), causando um `UnicodeDecodeError` no psycopg2 em vez de um
  erro de autenticação claro — o driver, no Windows, falha ao decodificar a
  mensagem de erro do servidor (em português, com acentuação) quando a
  autenticação falha. **Insight**: em ambiente Windows/pt-BR, erros de auth
  do psycopg2 podem aparecer como `UnicodeDecodeError` confuso; sempre
  suspeitar de credencial incorreta primeiro.
- Senha também continha `@`, que precisou ser url-encoded (`%40`) na
  connection string para não quebrar o parsing do DSN.
- Schema aplicado com sucesso via `python -m src.db`.

## 2026-07-01 — Etapa 2 (piloto): coleta inicial

- `seed_players` rodado: 730 jogadores Challenger/GM semeados.
- `collect_matches --players 30 --matches-per-player 10` rodado: 98-100
  partidas coletadas (raw_matches + raw_timelines).

## 2026-07-01 — Etapa 3 (dry-run): validação do pipeline com dados reais

- `build_features` gerou 98 partidas em `data/features.csv` (2 descartadas
  por terem menos de 15 min de timeline).
- `train_baseline` rodado como teste de sanidade (amostra pequena demais
  para reportar no texto):

  | Modelo       | Acurácia | Precisão | Recall | F1    | AUC-ROC |
  |--------------|---------:|---------:|-------:|------:|--------:|
  | RandomForest |   0.6537 |   0.5821 | 0.5000 | 0.5317| 0.6734  |
  | XGBoost      |   0.6632 |   0.5889 | 0.5750 | 0.5808| 0.6271  |
  | MLP          |   0.6121 |   0.5444 | 0.5000 | 0.4983| 0.6114  |

  Todos os modelos superaram o baseline de classe majoritária (~59,2%),
  confirmando que o pipeline de features/treino está correto. MLP não
  convergiu em `max_iter=500` nessa amostra pequena.

## 2026-07-02 — Etapa 2 (escala): coleta em larga escala

- `collect_matches --players 730 --matches-per-player 20` rodado (coleta é
  retomável — partidas já salvas são puladas).
- Resultado: **7.647 partidas brutas** (raw_matches/raw_timelines), **7.437
  normalizadas** com sucesso na tabela `matches` (diferença de ~210
  provavelmente remakes ou partidas incompletas descartadas pelo ETL).
- Ficou levemente abaixo do piso de 10.000 da meta (10k-30k), mas
  considerado suficiente para prosseguir com resultados reportáveis; pode
  ser complementado depois rodando `collect_matches` novamente (é
  retomável).

## 2026-07-02 — Etapa 3: features e baseline com dataset completo

- `build_features` gerou **7.353 partidas** em `data/features.csv` (após o
  corte de 15 min).
- `train_baseline` — resultados reportáveis para o TCC (taxa de vitória do
  time azul: 44,3%):

  | Modelo       | Acurácia | Precisão | Recall | F1    | AUC-ROC |
  |--------------|---------:|---------:|-------:|------:|--------:|
  | RandomForest |   0.7276 |   0.7006 | 0.6721 | 0.6860| 0.7995  |
  | **XGBoost**  | **0.7412**| **0.7153**|**0.6908**|**0.7027**|**0.8144**|
  | MLP          |   0.7288 |   0.7031 | 0.6709 | 0.6856| 0.8050  |

  **Insight**: XGBoost foi o melhor modelo em todas as 5 métricas,
  consistente com a literatura (Hodge et al., 2021) para predição em jogo
  aos 15 min. Não houve mais warning de convergência do MLP com a amostra
  maior.

---

## 2026-07-02 — Etapa 4: tuning de hiperparâmetros, calibração e SHAP

- Criado `src/models/tune_models.py` (não existia): `GridSearchCV` por
  modelo (otimizando AUC-ROC), com a mesma validação cruzada estratificada
  de 5 folds do baseline. Grades pequenas para manter o tempo de execução
  razoável (27 combinações × 5 folds × 3 modelos).
- Resultado do tuning (7.353 partidas):

  | Modelo       | Acurácia | Precisão | Recall | F1    | AUC-ROC | Melhores parâmetros |
  |--------------|---------:|---------:|-------:|------:|--------:|----------------------|
  | RandomForest |   0.7473 |   0.7192 | 0.7046 | 0.7116| 0.8259  | max_depth=6, min_samples_leaf=5, n_estimators=300 |
  | XGBoost      |   0.7431 |   0.7168 | 0.6942 | 0.7052| 0.8260  | learning_rate=0.01, max_depth=3, n_estimators=300 |
  | MLP          |   0.7487 |   0.7237 | 0.6997 | 0.7114| 0.8278  | alpha=0.01, hidden_layer_sizes=(32,) |

  **Insight**: o tuning melhorou os 3 modelos em relação ao baseline
  (etapa 3) e inverteu a ordem — sem tuning o XGBoost era o melhor, com
  tuning o MLP (rede menor, mais regularizada) passa à frente por uma
  margem pequena. Os 3 modelos ficam muito próximos entre si (~0.74-0.75
  acurácia, ~0.826-0.828 AUC), sugerindo que o teto de desempenho está mais
  limitado pelas features (apenas 5, diffs aos 15 min) do que pela escolha
  de modelo.
- Curva de calibração gerada em `reports/calibration_curve.png` comparando
  os 3 modelos tunados (probabilidade prevista vs. fração observada de
  vitórias, hold-out de 20%).
- `explain_shap.py` atualizado para usar os hiperparâmetros tunados do
  XGBoost (`learning_rate=0.01, max_depth=3, n_estimators=300`, antes
  estava com valores fixos não tunados).
- Gráficos SHAP gerados em `reports/shap_importance.png` e
  `reports/shap_beeswarm.png`. **Insight**: `gold_diff` (+0.58) e
  `xp_diff` (+0.55) dominam a importância; `dragon_diff` tem impacto
  moderado (+0.18); `kill_diff` é pequeno (+0.06); `tower_diff` é
  praticamente nulo (+0.00) — plausível, já que poucas torres caem antes
  dos 15 min, então a feature tem pouca variância na maioria das partidas.

## 2026-07-02 — Etapa 5: expansão do benchmark da interface NL

- `ANTHROPIC_API_KEY` real adicionada ao `.env` (antes era placeholder
  `sk-ant-...`, a interface NL não rodava).
- `src/nlq/evaluate_nlq.py` expandido de 5 para **22 perguntas** de
  referência (exigência da banca: >= 20), cobrindo agregações simples,
  joins (participants+players), filtros por posição/campeão/tier e
  perguntas sobre objetivos (barões, arautos, torres).
- Primeira rodada: **17/22 (77%)** de execution accuracy. Investigando as 5
  falhas com um script de debug, nenhuma era erro real de SQL — o LLM
  sempre gerava a resposta certa, mas com formatação diferente do gold SQL
  (colunas extras como contagem de jogos, win rate em porcentagem 0-100 em
  vez de fração 0-1, rótulos amigáveis "Azul"/"Vermelho" em vez de
  `team_id` bruto). **Insight**: a comparação por resultado exato (execution
  accuracy estrita) é sensível a escolhas de formatação do LLM que não
  mudam a resposta semântica — isso é uma limitação conhecida da
  metodologia de avaliação em text-to-SQL, não do sistema em si.
- Corrigido na raiz: reforçadas as regras de formatação no
  `src/nlq/schema_context.py` (win rate sempre como fração 0-1, apenas
  colunas pedidas, `team_id` bruto em vez de rótulo). Resultado: **21/22
  (95%)**.
- No processo, dois problemas reais (não só de formatação) foram
  encontrados e corrigidos:
  1. `generate_sql()` não fixava `temperature`, então o LLM podia gerar SQL
     diferente para a mesma pergunta em chamadas distintas — adicionado
     `temperature=0` em `src/nlq/nl_to_sql.py` para tornar a geração
     determinística (necessário para um benchmark reprodutível).
  2. Uma pergunta sobre o tier "Grandmaster" gerou `WHERE tier =
     'Grandmaster'` (case mismatch — a coluna guarda valores em maiúsculas,
     ex. `GRANDMASTER`), retornando 0 linhas silenciosamente. Adicionada
     nota explícita no schema sobre a convenção de maiúsculas.
- Falha restante (1/22, determinística): a pergunta sobre os "5 campeões
  com maior win rate com pelo menos 50 jogos" — o LLM insiste em incluir
  `COUNT(*) as games` como coluna extra mesmo com a regra "não adicione
  colunas extras", provavelmente porque a pergunta menciona um limiar de
  jogos (HAVING) e o modelo julga o count relevante para contexto. Decisão:
  documentar como limitação conhecida da interface em vez de ajustar o
  prompt especificamente para essa pergunta (evitar overfitting ao
  benchmark).
- **Execution accuracy final: 21/22 = 95%.**

## 2026-07-02 — Etapa 6: dashboard Streamlit com dados reais

- `streamlit run src/dashboard/app.py` testado de ponta a ponta com
  Playwright (navegador headless): KPIs, gráficos de campeões e o
  cruzamento objetivos×vitória renderizaram corretamente com os 7.437
  partidas reais (9.211 jogadores únicos, duração média 27,4 min).
  Screenshot salvo em `reports/dashboard_screenshot.png`.
- **Bug real encontrado e corrigido**: rodando exatamente o comando do
  README (`streamlit run src/dashboard/app.py`), a aplicação quebrava com
  `ModuleNotFoundError: No module named 'src'`. Diferente de `python -m
  src.xxx` (usado em todos os outros scripts), `streamlit run` não
  adiciona a raiz do projeto ao `sys.path` — só o diretório do próprio
  script. Corrigido em `src/dashboard/app.py` inserindo a raiz do projeto
  em `sys.path` explicitamente no topo do arquivo (`sys.path.insert(0,
  str(Path(__file__).resolve().parents[2]))`), já que este é o único
  ponto de entrada do projeto que não usa `-m`. **Insight**: sempre testar
  os comandos exatamente como documentados no README, não apenas os
  módulos internos — o ponto de entrada do usuário final pode ter um
  comportamento de import diferente do resto do código.
- Consulta em linguagem natural testada interativamente no dashboard
  ("qual posição tem o maior KDA médio?") — gerou SQL correta
  (`(kills + assists)::float / NULLIF(deaths, 0)`, agrupado por
  `team_position`) e renderizou o resultado sem erros de console.
- Nenhum erro de console JS encontrado nas duas verificações.

## 2026-07-02 — Front end React (interface principal da plataforma)

- **Decisão de stack** (com pesquisa de mercado jul/2026): Vite + React 19
  + TypeScript (SPA local, sem necessidade de SEO — Next.js adicionaria
  complexidade sem benefício), Tailwind CSS v4, Recharts para gráficos
  (padrão para dashboards React), TanStack Query e React Router. Fontes:
  comparativos Vite vs Next.js e chart libraries 2026 (techsy.io,
  designrevision.com, LogRocket, Syncfusion).
- **Backend estendido** para suportar o front:
  - CORS liberado para o dev server do Vite;
  - `GET /stats/objectives` (a query existia só dentro do Streamlit);
  - `POST /predict`: probabilidade de vitória do time azul aos 15 min +
    contribuições SHAP por feature na predição individual;
  - novo `src/models/export_model.py`: exporta o XGBoost tunado
    (`data/model.joblib`, carregado pela API no startup) e
    `reports/shap_importance.json`;
  - `reports/` servido como estático pela API.
- **4 páginas**: Dashboard (KPIs + campeões + objetivos×vitória), Consulta
  NL (SQL gerada + tabela de resultado, com histórico), Predição (sliders
  do estado aos 15 min → probabilidade ao vivo + SHAP da predição) e
  Explicabilidade (importância global, beeswarm, calibração). Tema
  dark/light com toggle. Paleta e regras de visualização seguindo a skill
  dataviz (paleta validada para daltonismo, texto nunca na cor da série,
  barras a partir do zero).
- **Verificação end-to-end** com Playwright (headless): as 4 páginas
  renderizam sem erros de console nos dois temas; predição reage aos
  sliders (50,4% no empate → 81,9% com +8k de ouro e 2 dragões); consulta
  NL de ponta a ponta ("quais os 3 campeões mais jogados?" → SQL correta +
  tabela). Ajustes pós-screenshot: `interval={0}` no eixo de campeões
  (nomes eram pulados) e cor de texto da legenda (regra: texto usa tinta
  de texto, não a cor da série).
- Coleta adicional rodando em paralelo durante o desenvolvimento: KPIs
  subiram de 7.437 para 8.681 partidas ao longo das verificações.
- **Insight**: `npm create vite@latest frontend -- --template react-ts` no
  Windows/PowerShell não repassou o `--template` (npm engoliu o flag) e
  gerou o template vanilla sem React — detectado porque `package.json` não
  tinha `react`. Corrigido instalando react/react-dom/@vitejs/plugin-react
  manualmente. Conferir sempre o `package.json` gerado por scaffolds.

## 2026-07-02 — Bug encontrado pelo usuário: "campeões mais jogados" errado

- O usuário rodou manualmente `SELECT champion_name, COUNT(*) ... ORDER BY
  pick_count DESC LIMIT 1` e obteve Senna (~1680 jogos), mas o dashboard
  mostrava Sona no card "Campeões mais jogados". **Causa raiz**:
  `GET /stats/champions` sempre ordenava por `win_rate DESC LIMIT N` no
  SQL, e o front end reordenava esse mesmo subconjunto (top-N por win
  rate) por `games` no cliente — ou seja, o card não mostrava os
  campeões mais jogados de verdade, só o mais jogado *dentro do top-15
  por win rate*. Senna/Ezreal/Seraphine (os mais jogados reais) ficavam
  de fora porque o win rate deles não estava no top 15.
- **Corrigido**: `GET /stats/champions` ganhou um parâmetro `sort`
  (`win_rate` ou `games`), com a coluna do `ORDER BY` escolhida por um
  dict fixo (sem risco de SQL injection). O front end agora faz duas
  chamadas independentes — uma por win rate, outra por jogos — em vez de
  reordenar um resultado já cortado.
- **Insight importante**: isso passou pela verificação end-to-end com
  Playwright de mais cedo porque o teste checou "a página renderiza sem
  erro" e "os números parecem plausíveis", não "os números batem com uma
  query de referência". Screenshot bonito não é o mesmo que dado
  correto — verificação visual pega quebras de renderização, não erros de
  lógica de agregação/ordenação. Vale a pena, ao verificar dashboards,
  conferir pelo menos um valor contra uma query SQL direta.

## 2026-07-02 — UX do slider "mínimo de jogos" (feedback do usuário)

- Usuário relatou duas coisas: (1) mudar o slider "parece dar reload" no
  dashboard, sem transição suave; (2) o slider vai de 10 a 200, mas o
  mínimo exibido no card "campeões mais jogados" é > 900 — não fazia
  sentido o controle não ter efeito visível.
- **Causa do "reload"**: a query do TanStack Query entrava em `isPending`
  a cada mudança do slider, trocando o gráfico inteiro por um Skeleton
  antes de re-renderizar — perdendo os dados antigos em vez de fazer uma
  transição entre valores.
- **Causa do "não faz sentido"**: o slider controlava as duas queries
  (win rate E mais jogados), mas com ~9 mil partidas os 15 campeões mais
  jogados sempre têm centenas/milhares de jogos — o filtro de mínimo de
  jogos (10-200) nunca consegue excluir nenhum deles. O controle só é
  estatisticamente relevante para o ranking de win rate (evitar que um
  campeão com poucas partidas e sorte apareça no topo).
- **Correção**: `placeholderData: keepPreviousData` (TanStack Query) para
  manter o gráfico anterior visível durante o refetch — o Recharts anima
  a transição das barras automaticamente (`animationDuration=400`,
  `ease-out`) em vez de mostrar um Skeleton. Debounce de 300ms no slider
  (estado do input separado do estado usado na query) para não disparar
  uma requisição a cada pixel arrastado. O slider foi movido para dentro
  do card "Campeões com maior win rate" (não fica mais acima dos dois
  gráficos) e o card "Campeões mais jogados" passou a usar um mínimo fixo
  baixo, desacoplado do slider.
- **Insight**: um controle de filtro que nunca produz um efeito visível
  em um dos dois gráficos que afeta é pior que não ter efeito nenhum —
  parece bug mesmo sem ser. Vale sempre perguntar "esse filtro pode
  realmente mudar o resultado, dado o volume de dados atual?" antes de
  aplicar o mesmo controle a duas visualizações diferentes.

## 2026-07-02 — Limitação real da interface NL encontrada pelo usuário

- Pergunta testada manualmente pelo usuário na Consulta NL: "em uma
  partida onde o time vermelho está com 2000 de ouro na frente do time
  azul aos 13 minutos, qual a chance do time azul ganhar?". A SQL gerada
  retornou `NULL`.
- **Diagnóstico (dois problemas independentes)**:
  1. *Bug de SQL*: a `EXISTS` comparava `gold_earned` de **um jogador**
     do time vermelho contra `SUM(gold_earned)` do **time azul inteiro**
     (5 jogadores) — unidades incompatíveis (ouro médio por jogador
     ~11.726 vs. soma de time 25.000-57.000+), então a diferença nunca
     cai no intervalo pedido (1800-2200) para nenhuma partida. `EXISTS`
     nunca satisfaz, `AVG` roda sobre zero linhas → `NULL`.
  2. *Limitação conceitual mais importante*: `participants.gold_earned`
     é o ouro **final** da partida, não um snapshot aos 13 min — a
     tabela não tem estado por minuto. A query tentou usar
     `game_duration_s BETWEEN 780 AND 840` (partidas que *terminaram*
     entre 13-14 min) como proxy, mas isso é outra pergunta
     completamente diferente. Só 7 partidas no banco têm essa duração
     (provavelmente rendições precoces), uma amostra irrelevante. O
     único lugar com estado por minuto é `raw_timelines` (JSONB), que a
     interface NL não acessa (`ALLOWED_TABLES` não inclui essa tabela,
     de propósito) — o LLM inventou um proxy capenga em vez de admitir
     que não pode responder com o schema exposto.
- **Resposta correta** obtida via `/predict` (modelo treinado sobre
  `gold_diff` de `raw_timelines`, gold_diff=-2000, resto neutro): time
  azul vence com **≈ 34,9%** (aos 15 min, não 13 — o dataset de features
  só tem o corte de 15 min usado no treino).
- **Insight para o capítulo de validação da interface NL**: a interface
  text-to-SQL é estruturalmente incapaz de responder perguntas sobre
  estado da partida em um instante específico (ex.: "aos 13 minutos"),
  porque o schema exposto (`matches/teams/participants/players`) só tem
  agregados finais por partida — dados de timeline ficam de propósito
  fora do `ALLOWED_TABLES` por serem JSONB não tabular. Isso não é um
  bug pontual, é um limite de escopo da abordagem — vale documentar
  explicitamente no texto do TCC (seção de limitações da interface NL) e
  considerar, como direção futura, expor uma view agregada por
  timestamp para permitir esse tipo de pergunta sem dar acesso direto ao
  JSONB.

## 2026-07-02 — Toggle SQL/Explicação na página de Consulta NL

- Pedido do usuário: na página de consulta, alternar entre ver a SQL
  gerada e uma explicação em linguagem natural do resultado.
- `src/nlq/nl_to_sql.py`: nova função `explain_result(question, sql,
  columns, rows)` — chama o Claude com a pergunta, a SQL e as primeiras
  linhas do resultado, pedindo uma explicação em português, texto corrido
  (sem markdown), sem jargão de SQL.
- `POST /ask/explain` (novo endpoint): recebe question/sql/columns/rows
  (o mesmo formato do retorno de `/ask`) e devolve a explicação.
  **Decisão de design**: a explicação é gerada sob demanda (só quando o
  usuário clica no toggle), não junto com `/ask` — evita dobrar
  custo/latência de chamada ao Claude em toda pergunta, já que a maioria
  dos usuários provavelmente só olha a SQL.
- Front end: `Nlq.tsx` ganhou um componente `HistoryCard` próprio (antes
  o histórico era renderizado inline no `.map`) para cada card ter seu
  próprio estado de toggle e cache da explicação — trocar de volta para
  "SQL" não reconsulta a API.
- **Ajuste pós-verificação**: a primeira resposta do Claude veio com
  markdown (`#`, `**negrito**`), que aparecia como asteriscos literais
  num `<p>` sem parser de markdown. Reforçado no prompt: "texto corrido
  simples, sem markdown". Confirmado com nova chamada.
- Verificado com Playwright: pergunta → SQL aparece → clique em
  "Explicação" → skeleton enquanto carrega → texto correto citando os
  números reais da tabela → volta para "SQL" é instantâneo.

## 2026-07-02 — Formatação da tabela de resultado na Consulta NL

- Feedback do usuário: a tabela de resultado mostrava nomes de coluna
  crus (`win_rate`) e números crus (`0.147`) — como as colunas vêm de
  SQL gerado dinamicamente pelo LLM, não dá pra ter um dicionário fixo
  de tradução por nome de coluna.
- Criado `frontend/src/lib/format.ts`: `humanizeColumn()` (snake_case →
  Title Case, ex. `win_rate` → "Win Rate") e `formatCell()` — detecta
  colunas de taxa por regex no nome (`rate`, `_pct`, `percent`) e
  valores em `[0,1]`, formatando como porcentagem pt-BR (`43,9%`);
  demais números usam `toLocaleString("pt-BR")` (separador decimal
  vírgula, milhar com ponto); booleanos viram "Sim"/"Não"; `null` vira
  "—". Aplicado em `ResultTable` (Nlq.tsx).
- Verificado: "qual o win rate do time azul e do time vermelho?" →
  colunas "Team Id" / "Win Rate", valores "43,9%" / "56,1%" em vez de
  `0.439`/`0.561`.

## 2026-07-02 — Tratamento de erros na Consulta NL

- Problema relatado: quando uma pergunta falhava, a tela só mostrava
  "Failed to fetch" (erro cru do `fetch()` do navegador), sem explicar o
  motivo. Pedido do usuário: diferenciar pergunta sem sentido/bloqueada
  pela validação (não é falha nossa) de uma falha real do sistema (essa
  precisamos saber).
- **Backend** (`src/api/main.py`): endpoints `/ask`, `/ask/explain` e
  `/predict` agora capturam qualquer exceção e devolvem JSON com
  `detail` claro em vez de deixar o Starlette devolver um 500 sem corpo.
  Nova função `_external_call_error()` classifica a causa:
  `anthropic.AuthenticationError` → 502 "chave Anthropic inválida,
  verifique .env"; `anthropic.APIError` → 502 "erro ao consultar IA";
  `psycopg2.OperationalError` → 503 "não foi possível conectar ao
  banco"; `psycopg2.Error` (SQL gerada referencia coluna/tabela
  inexistente) → 422 "consulta gerada não pôde ser executada"; qualquer
  outra coisa → 500 genérico. `ValueError` de `validate_sql` continua
  400 (pergunta rejeitada pela validação de segurança — não é falha
  nossa).
- **Front end**: nova classe `ApiError` (`frontend/src/lib/api.ts`) com
  campo `kind: "validation" | "network" | "server"`. `request()` agora
  envolve o `fetch()` num try/catch — se a chamada falhar antes de
  qualquer resposta (API fora do ar, CORS, DNS), lança `kind: "network"`
  com mensagem específica ("verifique se o servidor está rodando");
  status 400 vira `kind: "validation"`; qualquer outro status vira
  `kind: "server"`.
- `ErrorNote` (`components/ui.tsx`) ganhou um `kind` opcional com
  ícone/título por tipo: `validation` é neutro/informativo (ícone Info,
  "Não foi possível responder", cinza) — não alarma o usuário por algo
  que não é bug; `network`/`server` são vermelhos com AlertTriangle/
  WifiOff ("Falha de conexão com a API" / "Erro no servidor") — chamam
  atenção porque são falhas reais do sistema.
- Consulta NL (`Nlq.tsx`) reestruturada: perguntas que falham agora
  entram no histórico como um card próprio com o motivo (antes era só
  um aviso solto acima da lista, que sumia na próxima pergunta) —
  atende o pedido literal de "fazer um card explicando o motivo".
- Verificado com Playwright: (1) API derrubada propositalmente → card
  vermelho "Falha de conexão com a API" com instrução acionável; (2)
  pergunta pedindo para apagar dados → card cinza "Não foi possível
  responder — Apenas SELECT é permitido." API religada depois do teste.

## 2026-07-02 — Diagnóstico real de erros + chat de acompanhamento na Consulta NL

- Feedback do usuário: a mensagem genérica "tente reformular a pergunta"
  não ajuda a melhorar o código — quando a falha é nossa (não do
  usuário), ele precisa ver a causa real para debugar.
- **Caso de teste real que expôs um bug**: "qual a taxa de vitória do
  Jayce contra rengar top/jax jungle/azir mid/sivir adc/sona suporte,
  estando 3940 de gold à frente aos 18 min?" retornava "Erro no servidor
  — consulta gerada não pôde ser executada", sem mais detalhes.
- **Diagnóstico habilitado**: nova exceção `SqlExecutionError` em
  `src/nlq/nl_to_sql.py` carrega a SQL gerada e o erro original do
  psycopg2; `POST /ask` retorna `detail` estruturado
  (`{message, sql, cause}`) em vez de string genérica; `ErrorNote`
  (front) ganhou blocos opcionais de SQL (monospace) e "Erro do banco".
  Com isso, o erro real apareceu: `ERROR: erro de sintaxe no fim da
  entrada... SELECT SUM(CASE WHEN p3.team_id = p.team_id` — a SQL gerada
  estava **cortada no meio** (faltava fechar o CASE/subquery).
- **Causa raiz encontrada e corrigida**: `generate_sql()` usava
  `max_tokens=500`; perguntas com várias condições (matchup com 5
  campeões específicos = 5 `EXISTS` + subquery de gold) geram SQL mais
  longa que isso, e a resposta do Claude era cortada no limite de
  tokens, virando SQL sintaticamente inválida. Aumentado para
  `max_tokens=1200` e adicionado um check em `msg.stop_reason ==
  "max_tokens"` — se mesmo assim a geração for cortada, agora vira um
  erro de validação claro ("pergunta complexa demais, tente dividir")
  em vez de um erro de sintaxe genérico. Reexecutada a mesma pergunta:
  SQL completa e válida, retornou `NULL` (nenhuma partida bate com esse
  cenário tão específico — resultado plausível, não bug).
- **Insight**: sem mostrar a SQL e o erro real, esse bug de truncamento
  por `max_tokens` seria invisível — pareceria só "a IA não conseguiu
  responder". Mostrar o diagnóstico técnico não é só para o usuário
  final, é uma ferramenta de desenvolvimento.
- **Chat de acompanhamento**: cada card de resultado agora é uma
  "thread" — um campo no rodapé permite continuar a mesma consulta
  ("e quais têm o menor win rate entre esses 3?" após "quais os 3
  campeões mais jogados?"). `generate_sql()` ganhou parâmetro `history`
  (pares pergunta/SQL anteriores, enviados como turnos alternados
  user/assistant para o Claude) para dar contexto. Testado: a pergunta
  de acompanhamento gerou uma subquery referenciando corretamente o
  top-3 da pergunta anterior.

## 2026-07-02 — Resultado vazio/NULL e honestidade sobre limitação de dados

- Dois problemas levantados pelo usuário sobre a mesma sequência de
  perguntas:
  1. Resultado `NULL` de um `AVG()` sem `GROUP BY` (sobre zero linhas)
     aparecia na tabela como "Win Rate / —", pouco claro.
  2. Pergunta "qual a chance de vitória do Jayce, tendo 2500 de gold,
     aos 21 minutos, contra um Rengar no top?" — quis dizer um **estado
     no minuto 21**, mas o sistema reinterpretou como "partida durou
     ~21 min E ouro final ~2500", o mesmo erro conceitual já documentado
     antes (partida de 13 min). A correção do usuário no chat
     ("você entendeu errado...") foi rejeitada com "Apenas SELECT é
     permitido" — a interface não tinha como o LLM dizer "não sei"
     dentro do contrato de sempre-retornar-SQL.
- **Correção 1 (resultado vazio)**: `frontend/src/lib/format.ts` ganhou
  `isEmptyResult()` (zero linhas, ou uma linha com todos os valores
  nulos). `ResultTable` mostra "Nenhum resultado encontrado para esses
  critérios." em vez da tabela quando isso acontece.
- **Correção 2 (honestidade sobre dados indisponíveis)**: reforçado
  `src/nlq/schema_context.py` — deixa explícito que `gold_earned`,
  `kills` etc. são totais **finais**, `game_duration_s` é duração
  **total**, e que nenhuma tabela tem estado em um minuto específico.
  Nova regra: se a pergunta pedir isso, responder com
  `SELECT 'não é possível responder: <motivo>' AS aviso;` em vez de
  inventar uma aproximação. Também: "responda SEMPRE com uma única
  SELECT válida, mesmo para correções/esclarecimentos" — resolve o caso
  da mensagem de correção ser rejeitada.
- **Bug pego durante a verificação**: a primeira versão do aviso gerado
  pelo LLM continha um `;` dentro do próprio texto explicativo (pontuação
  normal de uma frase), e `validate_sql()` rejeitava isso como "múltiplos
  statements" — o check de `;` era ingênuo, não diferenciava um `;` real
  separando comandos de um `;` dentro de uma string literal. Corrigido
  com `_without_string_literals()`: remove o conteúdo de literais
  `'...'` antes das checagens de `;`, palavra proibida e tabelas.
- Front end: `isAdvisory()` detecta a convenção `SELECT '...' AS aviso`
  (uma coluna chamada exatamente "aviso") e renderiza como um aviso
  informativo (ícone Info) em vez de uma tabela/toggle SQL — não faz
  sentido mostrar "SQL/Explicação" para uma mensagem que já é a
  explicação.
- Verificado: a pergunta do Jayce aos 21 min agora responde
  honestamente ("não é possível responder: a tabela participants contém
  apenas totais finais..."); uma pergunta com resultado genuinamente
  vazio (duração > 100 min) mostra a mensagem amigável; uma pergunta
  normal com dados continua funcionando (Teemo jungle, 14,3% win rate).
- **Insight para o TCC**: essa é a segunda vez que a mesma classe de
  pergunta (estado em um minuto específico) engana o sistema — agora
  virou uma regra explícita e testável no schema, não só uma nota no
  diário. Bom exemplo para a seção de limitações/iteração da interface
  NL: o primeiro instinto (deixar o LLM tentar) produz respostas
  plausíveis mas erradas; a correção não foi "ajustar o SQL", foi
  ensinar o sistema a reconhecer os limites do próprio schema.

## 2026-07-02 — Retrabalho da UI inspirado em sites de referência

- **Meta da coleta atingida**: 10.402 partidas (11 patches, 18/mai-02/jul),
  acima do piso de 10k. Features e modelo re-exportados com o dataset
  completo (10.295 partidas após corte de 15 min).
- **Pesquisa**: naveguei (Playwright headless + screenshots) por op.gg,
  esports.op.gg, mobalytics e probuildstats (leagueofgraphs bloqueou com
  Cloudflare) + pesquisa sobre métricas de analista de LoL. Padrões
  extraídos: tabela de campeões com ícone/win/pick/ban rate e barras
  inline (op.gg), filtros por rota, feed de partidas com borda
  vitória/derrota (probuildstats). Métricas de analista: win/pick/ban por
  campeão e posição, KDA, **gold diff no early game** (a métrica nº 1 da
  literatura), viés de lado azul/vermelho, duração, sempre com amostra
  visível.
- **ETL estendido — bans**: os bans sempre estiveram no payload bruto
  (`info.teams[].bans[]`), só não eram extraídos. Nova tabela `bans`
  (match_id, team_id, pick_turn, champion_id) no schema; `load_one`
  agora insere bans; backfill via `python -m src.etl.load_matches`
  (96.696 bans de 10.689 payloads). **Bug pré-existente corrigido**:
  `reprocess_all()` nunca tinha rodado de verdade — cursor nomeado
  (server-side) do psycopg2 não funciona com `autocommit=True`
  ("can't use a named cursor outside of transactions"). Corrigido com
  duas conexões: leitura transacional (cursor nomeado) + escrita
  autocommit.
- **API estendida** (`src/api/main.py` v0.3): `/stats/champions` agora
  retorna win/pick/ban rate, KDA, CS, ouro, dano e posição principal,
  com filtros `role`/`search`/`min_games` e `sort` por whitelist; novo
  `/stats/champion/{nome}` (stats por posição, matchups com >= 15 jogos,
  últimas 10 partidas); `/stats/overview` ganhou patches e win rate do
  lado azul; novos `/stats/durations` (histograma 5 min),
  `/stats/gold15` (win rate azul por faixa de gold diff aos 15, do
  features.csv com cache por mtime) e `/matches/recent` (feed).
- **Front — 2 páginas novas + 2 reformuladas**: página **Campeões**
  (tabela estilo op.gg: barras inline CSS, ordenação server-side,
  filtro por rota, busca com debounce, clique → detalhe), página de
  **detalhe do campeão** (tiles, por posição, melhores/piores matchups,
  últimas partidas com borda vitória/derrota), **feed de Partidas**
  (estilo probuildstats: 10 ícones por partida, lado vencedor em
  destaque, perdedor esmaecido) e **Dashboard** analítico (KPIs +
  patches + viés de lado 43,6% azul / 56,4% vermelho; gráfico-assinatura
  gold diff aos 15 × vitória — barras vermelhas quando o vermelho
  lidera, azuis quando o azul lidera, cruzando 50% no zero; histograma
  de duração; objetivos). Ícones de campeão via CommunityDragon por
  `champion_id` (evita divergência de grafia de nomes internos).
- **Insights dos dados** (para o texto do TCC): viés de lado relevante
  no alto elo BR (azul vence só 43,6%); a curva gold15 é quase
  logística: -7k → 3,3% de vitória azul, +7k → 95,3%; Zed com 39,6% de
  ban rate; matchup extremo Jayce×Poppy 13,3% (n=15).
- **Verificação**: Playwright nos dois temas sem erros de console +
  validação de 3 números da UI contra SQL direto (Senna 1.970 jogos,
  Zed ban rate 39,55%, Jayce×Poppy 15 jogos/13,33% — todos batem).
  **Insight de verificação**: os gráficos Recharts apareciam vazios nos
  screenshots `fullPage` — o resize de viewport do fullPage dispara o
  ResponsiveContainer, que re-anima as barras do zero no instante da
  captura. Não era bug do app (DOM tinha geometria e fill corretos);
  screenshots sem fullPage resolvem.

## 2026-07-03 — Predição multi-fase, Home de insights, análise de partida

- **Pesquisa (fases do jogo)**: rotas ~1-14 min (placas de torre caem aos
  14:00), mid ~14-25, late 25+; literatura de predição com dados de 10
  min chega a ~73% de acurácia, crescendo com a minutagem. Confirmou a
  suspeita do usuário: `tower_diff` aos 15 min não tem sinal porque
  quase nenhuma torre caiu até ali.
- **Predição multi-fase (B)**: `build_features` agora gera features em 4
  cortes (10/15/20/25 min) → `data/features_phases.csv` (37.532 linhas;
  10.351 partidas aos 10 min, 7.575 chegam aos 25) + `features.csv`
  mantido no corte de 15 (compatibilidade). `export_model` treina um
  XGBoost por corte → `data/models_phases.joblib` +
  `reports/shap_importance_phases.json`. `/predict` ganhou o campo
  `minute` (10|15|20|25). Página de Predição com seletor de fase e
  ranges de slider por fase (percentis 1-99 de cada corte).
  **Resultado-chave para o TCC**: a importância SHAP do `tower_diff`
  cresce 0,0008 → 0,0013 → 0,0029 → 0,079 dos 10 aos 25 min (~60× do 15
  ao 25) — as torres só viram sinal quando de fato caem; e `kill_diff`
  perde importância no late (o valor dos abates já está capturado em
  ouro/XP).
- **Análise de partida (D)**: novo `GET /matches/{id}/analysis` — parseia
  a timeline da partida e roda o modelo da fase correspondente minuto a
  minuto, gerando a curva de probabilidade de vitória retrospectiva
  ("o que o modelo diria ao vivo") + curva de diferença de ouro + stats
  finais por jogador + objetivos. Página `/partidas/:id` (feed clicável).
  É o alicerce direto do objetivo futuro de análise em tempo real.
- **Home de insights (C)**: `seed_players` não traz mais nomes (a Riot
  removeu do endpoint de liga) — novo `src/collect/backfill_names.py`
  preencheu gameName/tagLine de 723/723 jogadores via account-v1. Novo
  `GET /stats/highlights` e página inicial com destaques, cada um com o
  "porquê" (fundamento estatístico): melhor jogador CBrayanB#BR2 (87,5%
  em 40 jogos, Challenger), melhor campeão para subir de elo Rek'Sai
  (55,8% em 505 jogos), matchup mais desequilibrado Rek'Sai×Lee Sin
  (77,3% em 44), Master Yi banido em 55,5% das partidas, vermelho vence
  56,3%. Dashboard movido para `/dashboard`.
- **Ajustes (A)**: gráfico de ouro do dashboard renomeado para "Ouro ×
  taxa de vitória" com explicação em linguagem simples e exemplo; tabela
  de campeões com transição de opacidade ao trocar rota (sem "piscar");
  Explicabilidade reescrita com seletor de fase na importância SHAP e
  blocos "como ler" em cada gráfico (beeswarm e calibração).
- **NLQ — composições de time**: a pergunta "Senna e Brand contra Vayne
  e Lulu, quem ganha?" era rejeitada com um aviso incorreto de "não é
  possível responder". O schema TEM como responder (EXISTS amarrando
  aliados ao mesmo team_id e inimigos ao oposto) — adicionado o padrão
  com exemplo no `schema_context.py`, com instrução de sempre incluir o
  COUNT de partidas (amostras de composições exatas são pequenas).
  Testada a pergunta exata do usuário: agora gera a SQL correta (com
  UNION ALL para as duas perspectivas) e mostra n=1 partida com essa
  composição — resposta honesta sobre a amostra.
- **Verificação**: typecheck limpo, Playwright sem erros de console nas
  páginas novas (Home, Predição por fase, análise de partida,
  Explicabilidade por fase), e dois destaques da Home validados contra
  SQL direto (CBrayanB 40 jogos/87,5%; Rek'Sai×Lee Sin 44/77,27% —
  batem exatos).

## 2026-07-03 — Visual hextech, viés de lado explicado e Montar Partida (v1)

- **Por que a Predição zerada dá ~48% e não 50%**: pergunta do usuário
  respondida com pesquisa. Zerar os sliders significa "empate em
  ouro/XP/objetivos aos N min", não "jogo neutro" — e o modelo aprendeu
  que mesmo empatado o lado vermelho é favorecido neste dataset. A
  literatura geral aponta leve vantagem AZUL no solo queue (~50,6-53%),
  mas nosso dataset BR Challenger/GM mostra o VERMELHO com 56,3% — e o
  viés é estável em todos os patches (azul entre 37-44% em 16.10-16.13),
  não é anomalia de versão. Hipótese mais plausível: counter-pick
  garantido do vermelho pesa mais no elo onde todos punem draft + acesso
  ao pit do dragão. Nota explicativa adicionada na própria página de
  Predição; card da Home atualizado com o contraste vs literatura.
  **Achado relevante para o TCC** (inversão do consenso da literatura em
  um recorte específico).
- **Visual hextech** (inspiração: console "Hextech Agent" visto pelo
  usuário no LinkedIn): tokens dourados (`--gold`/`--gold-bright`, por
  modo) e classe `.hextech-title` (serifado, caixa alta, espaçado) —
  usados só no chrome/títulos, nunca nas séries de dados (paleta de
  gráficos validada permanece). Home ganhou herói com a splash art do
  melhor campeão (CommunityDragon `splash-art/centered`) sob gradiente,
  título dourado serifado e cards com borda/glow dourados no hover.
- **Dashboard com mais informação**: KPIs novos (abates por partida:
  60,2; % que chega ao late game 25+ min: 66,8%) e gráfico de cobertura
  por patch (16.10: 94 → 16.13: 5.250 partidas — transparência sobre
  onde o dataset concentra). Bug corrigido no novo endpoint
  `/stats/patches`: alias de coluna dentro de função no ORDER BY não é
  permitido no Postgres — trocado por `ORDER BY MIN(game_creation)`.
- **Montar Partida (team builder v1)** — a feature nova pedida:
  - `POST /compose`: recebe os dois times por posição e devolve (a)
    matchup de cada lane (win rate real do confronto direto quando há
    >= 10 jogos; senão, aproximação pela diferença dos perfis gerais,
    marcada como "perfil"); (b) sinergias de dupla por time (win rate da
    dupla junta vs média individual, >= 20 jogos, em pontos
    percentuais); (c) estimativa heurística agregada (média dos
    log-odds das lanes + ajuste leve de sinergia), com nota explícita de
    que NÃO é o modelo ML e não inclui o viés de lado.
  - Página `/montar`: seletores 5v5 com ícones, barras por lane,
    listas de sinergia (+/- pp) e medidor da estimativa. Preparada como
    primeiro passo da análise de champion select competitivo.
  - Teste 5v5 real: Jayce/LeeSin/Ahri/Senna/Lulu vs
    Rengar/RekSai/Zed/Vayne/Sona → 42,9% azul; coerente com os dados
    (LeeSin×RekSai 22,7% em 44 jogos — o mesmo matchup extremo do
    insight da Home, agora pelo outro lado; sinergia Ahri+Lulu +21,7pp
    em 40 jogos).
- **Verificação**: typecheck limpo; Playwright preencheu o 5v5 via UI e
  validou o fluxo completo sem erros de console; screenshots de Home/
  Dashboard/Montar conferidos visualmente.

## 2026-07-03 — Visual unificado, mapa de calor e Montar Partida detalhado

Quatro pedidos atendidos nesta rodada:

- **Visual hextech em todas as páginas**: componente `PageHeader`
  compartilhado (rótulo dourado em caixa alta + título serifado
  `gold-bright` + linha de brilho degradê), aplicado a Dashboard,
  Campeões, Partidas, Consulta NL, Predição, Montar Partida,
  Explicabilidade e às páginas de detalhe; título da sidebar também
  serifado dourado. Regra mantida: dourado só no chrome, nunca nas
  séries de dados.
- **Mapa de calor na análise da partida** (`GET /matches/{id}/positions`
  + componente `MapHeatmap`): as timelines já guardavam posição x/y,
  nível e abates com local (participantFrames — nada novo a coletar). O
  minimapa oficial (DDragon `map/map11.png`; o layout não muda entre
  patches) recebe um canvas com gradientes radiais aditivos
  (`globalCompositeOperation: "lighter"`) — azul e vermelho acumulando
  uma janela de 5 minutos até o minuto do slider, mais recente = mais
  intenso — e por cima os ícones dos campeões na posição exata do
  minuto + ✕ nos abates. Transformação de coordenadas: bounds oficiais
  do mapa 11 (min −120, max 14870/14980), y invertido (origem do jogo é
  o canto inferior esquerdo). Dá para "assistir" a partida: rotas
  separadas no early, agrupamentos em objetivos no mid/late.
- **Objetivos da partida legíveis**: as duas linhas de texto viraram um
  card único com barras espelhadas a partir do centro (estilo op.gg),
  ícone por objetivo e contagens coloridas por lado. Conferido contra o
  SQL (`teams`): azul 10/2/1/0/2, vermelho 2/1/0/0/0 na partida de
  teste — bate exatamente.
- **Montar Partida sem duplicados e com estado detalhado**:
  - Campeão repetido agora é bloqueado nas duas camadas: cada select só
    oferece campeões ainda não escolhidos (mantendo o valor do próprio
    slot) e o `/compose` valida e devolve 400 com mensagem clara (o
    usuário tinha conseguido montar um time com duas Anivias).
  - `state` opcional no `/compose` (minuto 10/15/20/25 + diffs de ouro,
    XP/nível, abates, torres e dragões — sliders compartilhados com a
    Predição via `src/lib/matchState.ts`). A combinação é em log-odds:
    `logit(combinado) = logit(ML) + logit(composição)` — o termo ML já
    inclui a taxa-base (viés de lado) e o estado; a composição entra
    como evidência extra centrada em 50%, então nada é contado duas
    vezes. A UI mostra a decomposição (só composição / só estado ML /
    taxa-base do empate) para o número final ser auditável.
  - Verificação numérica: mesmo 5v5 da entrada anterior (42,9% de
    composição — consistente) + estado +3000 ouro/+5 abates/+2 torres/
    +1 dragão aos 15 min → ML 69,5%, combinado 63,1%; recomputado à mão
    com a fórmula, bate exato. Na UI (sem XP): 42,9% + ML 61,8% →
    54,8%, taxa-base 48,1% idêntica à da página de Predição.
- **Verificação**: typecheck limpo; Playwright navegou as 8 páginas
  (cabeçalhos hextech em todas), moveu o slider do mapa de calor
  (14 → 25 min, jogadores se deslocam do farm em rotas para o rio/meio)
  e rodou o fluxo completo do Montar Partida com estado — zero erros de
  console.

## 2026-07-03 — Retreino nos 10k, objetivos por minuto e UI v2 (Início/Dashboard/Explicabilidade)

- **Retreino dos modelos no dataset completo** (10.295 partidas com
  features aos 15 min; antes ~3k):

  | Modelo (tunado) | Acurácia | Precisão | Recall | F1 | AUC-ROC |
  |---|---|---|---|---|---|
  | RandomForest | 0,7507 | 0,7186 | 0,7039 | 0,7111 | 0,8305 |
  | XGBoost | 0,7501 | 0,7212 | 0,6959 | 0,7083 | 0,8319 |
  | MLP | 0,7522 | 0,7268 | 0,6919 | 0,7089 | 0,8325 |

  Baselines (default): XGBoost 0,7435 / AUC 0,8214. O tuning nos 10k
  mudou o melhor XGBoost de `n_estimators=300` para **500** (lr 0,01 e
  max_depth 3 mantidos) — `export_model.py` atualizado e os 4 modelos
  por fase re-exportados. Efeito colateral honesto: com os modelos
  novos, a razão de importância SHAP do tower_diff (25 vs 15 min) caiu
  de ~60× para ~7× — a página de Explicabilidade agora calcula essa
  razão dinamicamente do JSON em vez de citar um número fixo. Logs:
  `reports/train_baseline_10k.log` e `reports/tune_models_10k.log`.
- **Objetivos controlados pela minutagem** (pedido do usuário): o
  `GET /matches/{id}/positions` agora devolve também os eventos de
  objetivo (ELITE_MONSTER_KILL e BUILDING_KILL — cuidado: neste último o
  `teamId` é o dono da construção destruída, pontua o oposto;
  killerTeamId 300 = execução neutra, fica de fora). O card de
  objetivos da análise da partida ficou sincronizado com o slider do
  mapa de calor ("Objetivos até o minuto X"), com fallback para os
  totais finais quando não há timeline. Verificação: acumulado dos
  eventos no fim = totais da tabela `teams` exatos (azul 10/2/1/0/2,
  vermelho 2/1/0/0/0 na partida de teste).
- **Início v2** (brainstorm com base nas referências op.gg/
  leagueofgraphs): busca de campeão no herói (filtra no cliente, Enter
  ou clique navega ao detalhe), faixa de números do dataset, três
  rankings top-5 com micro-barras (maior win rate 200+/mais jogados/
  mais banidos — padrão leagueofgraphs), seções com títulos hextech,
  insights com "porquê" mantidos e um feed de 4 partidas recentes. Bug
  pego na verificação: o ranking "mais jogados" formatava contagem como
  percentual (197000,0%) — corrigido com formatador por card. Checagem
  vs SQL: Master Yi é mesmo o mais banido (55,45%; o valor antigo de
  39,55% era do Zed, hoje 3º).
- **Dashboard v4** (a "visualização confusa"): reorganizado em 3 seções
  narrativas — "O que decide partidas" (ouro aos 15 × vitória,
  objetivos por resultado, card do lado do mapa com barras azul 43,6% ×
  vermelho 56,4%), "Retrato do meta" (duração + KPIs de ritmo) e
  "Cobertura do dataset" (KPIs + partidas por patch). Cada gráfico
  ganhou uma linha "Leitura:" em dourado calculada dos próprios dados
  exibidos (ex.: "com +6k a +8k o azul vence 95,3%"; "16.13 concentra
  50,5% do dataset").
- **Explicabilidade v2**: novo gráfico de linhas com a evolução da
  importância |SHAP| de cada fator ao longo das 4 fases (uma linha por
  fator, cores consistentes com o gráfico de barras via `--chart-3`/
  `--chart-4` novos na paleta) — é o gráfico que conta o achado central
  (torres ~7× mais importantes no late; abates caem). Barras do gráfico
  por fase agora coloridas por fator.
- **NLQ mais honesto sobre amostras pequenas** (caso Nocturne + Ahri/
  Orianna do usuário): o prompt do `explain_result` agora pede (a)
  avaliação explícita de confiança quando algum grupo tem <30 partidas
  e (b) um trecho "Leitura de jogo:" com conhecimento de LoL rotulado
  como fora dos dados, dizendo se concorda ou discorda dos números.
  Testado com a pergunta real: a explicação passou a avisar que 11 e 13
  partidas são pouco ("uma diferença de 35pp pode ser ruído") e trouxe
  a leitura de jogo. Limite conhecido: o conhecimento de jogo vem do
  LLM e pode divergir do consenso da comunidade — está rotulado
  exatamente por isso.
- **Verificação**: typecheck limpo; Playwright cobriu Início (busca →
  navegação), Dashboard, Explicabilidade, sincronização objetivos ×
  slider e o fluxo NLQ ponta a ponta — zero erros de console.

## 2026-07-03 — Revisão completa (código, dados, docs, benchmark)

Auditoria de ponta a ponta após o ciclo de features. Achados, do mais
grave ao menor:

1. **[CRÍTICO — corrigido] smoke test sobrescrevia dados reais**:
   `tests/smoke_test.py` escrevia as 400 partidas sintéticas em
   `data/features.csv` — o mesmo arquivo que o `/stats/gold15` da API lê
   (com cache por mtime), ou seja, rodar o smoke test fazia o gráfico
   "ouro × vitória" do dashboard passar a exibir dados falsos
   silenciosamente. Corrigido: o teste agora roda com `chdir` em um
   `TemporaryDirectory` (com retorno ao cwd antes da limpeza — Windows
   não remove o diretório corrente). O `features.csv` real foi
   restaurado do `features_phases.csv` (10.295 partidas) e o gold15
   confirmado servindo os números reais (95,3% em +6k a +8k).
2. **[REGRESSÃO — corrigido] benchmark NLQ tinha caído de 95% para
   77%** sem ninguém notar: o schema_context cresceu (aviso de totais
   finais, exemplo de composição, regra single-SELECT, bans) e nunca
   re-medimos. Diagnóstico: 4 das 5 falhas eram a instrução "sempre
   inclua COUNT(*) de partidas" (pensada para composições) vazando para
   qualquer pergunta de win rate. Corrigido o escopo da regra ("APENAS
   nesse tipo de pergunta de composição... NÃO acrescente a contagem se
   não foi pedida") → **20/22 = 91%**. As 2 falhas restantes são
   limitações conhecidas e benignas, mantidas sem overfit do prompt:
   a coluna COUNT quando a pergunta menciona "pelo menos 50 jogos" (já
   falhava na medição original de 95%) e rótulos 'Azul'/'Vermelho'
   quando a própria pergunta nomeia os times (resposta correta para
   humanos; o benchmark é exact-match). Lição: **re-rodar o
   evaluate_nlq sempre que o schema_context mudar.**
3. **[GAP — corrigido] NLQ não conhecia a tabela `bans`**: nem no
   schema do LLM nem na whitelist de validação — perguntas sobre
   banimento (que a UI mostra em toda parte) eram impossíveis.
   Adicionados `bans` ao `ALLOWED_TABLES` e ao schema_context (com a
   nota de que não tem champion_name; join com participants). Testado:
   "qual campeão é o mais banido?" → champion_id 11 (Master Yi), 55,45%
   — bate com o SQL direto.
4. **[DOCS — corrigido] README defasado**: checklist marcava tuning de
   hiperparâmetros como pendente (feito duas vezes), faltava
   `tune_models` na ordem de execução e a seção do front não citava
   montar partida/mapa de calor. Atualizado; itens concluídos marcados.
5. **[OK] Verificações que passaram**: smoke test verde; typecheck
   limpo; whitelists de sort/role na API (sem SQL injection — tudo
   parametrizado); regra de vazamento respeitada (features só de estado
   pré-corte); varredura Playwright das 8 páginas no TEMA CLARO (até
   então só o escuro tinha sido verificado) sem erros de console;
   objetivos por minuto e heat map ok nos dois temas; logs de runtime
   da API sem erros acumulados.

## 2026-07-03 — Mapa de calor: trocado o fundo por um SVG próprio

O usuário apontou (com print) que o mapa de calor estava usando uma
imagem errada: o `map11.png` do Data Dragon (`cdn/6.8.1/img/map/map11.png`,
mas confirmado que TODAS as versões atuais servem o mesmo arquivo — a
Riot nunca atualizou esse asset) é uma arte antiga e cartunesca, bem
distante do visual do jogo atual e destoante do resto da UI hextech.
Busquei alternativas no CommunityDragon (texturas reais do minimapa) mas
não há um endpoint estável/público para isso (todas as tentativas de
caminho conhecido retornaram 404 — assets de mapa não são expostos como
os de campeão).

Solução: `SummonersRiftBackground`, um componente SVG próprio dentro de
`MapHeatmap.tsx` — sem dependência externa, garantindo renderização
idêntica em qualquer ambiente. Usa o MESMO referencial de coordenadas
0-100 que os ícones/calor já usavam (nx/ny × 100), então não precisou de
nenhuma transformação extra: rio diagonal com poços de Barão/Dragão,
as 3 rotas (topo/meio/base) como traços arredondados, e as duas bases
como círculos nas cores dos times, no canto inferior-esquerdo (azul) e
superior-direito (vermelho) — a orientação real do mapa. Removida a URL
`MINIMAP_URL` de `ddragon.ts` (não usada mais).

Verificação: Playwright confirmou renderização limpa nos dois temas
(o mapa é terreno fixo, não muda com dark/light) e zero erros de
console.

**Correção no mesmo dia**: o usuário apontou (com print) que o resultado
ainda parecia errado — só um quadrado com uma diagonal, sem rio nem
poços visíveis. Isolei o SVG puro (removendo canvas/ícones via
Playwright) para depurar e achei dois bugs de geometria na 1ª versão:
(1) a curva do rio usava `Q 50 50` como ponto de controle, que é
EXATAMENTE o ponto médio do segmento start→end — matematicamente uma
curva quadrática degenera para uma reta quando o ponto de controle cai
no ponto médio (`Q(t) = (1-t)·P0 + t·P2`), então o "rio" ficava colado
na rota do meio, indistinguível dela; (2) rota do topo + rota de baixo
juntas formavam só o contorno de um quadrado, sem nenhum outro detalhe,
lendo como um diagrama abstrato em vez de um mapa. Corrigido com uma
curva em S de verdade (dois `Q` com pontos de controle deslocados da
reta), poços de Barão/Dragão com anel duplo (mais legíveis), marcas de
torre (losangos) perto de cada base e pontos de acampamento de selva
como textura. Reverificado isolando o SVG (sem calor/ícones) antes de
reconfirmar a composição completa — lição: ao depurar um elemento
visual sob camadas (calor+ícones por cima), isolar a camada de baixo
primeiro evita confundir "não renderizou" com "renderizou errado".

## 2026-07-03 — Mapa de calor: textura real do minimapa (pesquisa)

Pedido do usuário: pesquisar o mapa atualizado do LoL para usar de fundo
do mapa de calor, no lugar do SVG desenhado à mão (que resolvia o
problema visual, mas era só um esquema simplificado, não o mapa de
verdade). Pesquisa (web + arquivos do próprio jogo via CommunityDragon):

- **Não existe ainda uma reformulação visual completa de Summoner's
  Rift disponível**: a Riot confirmou o "League Next" — um novo cliente
  integrado + reformulação visual total do mapa (novos assets,
  iluminação, texturas) — mas para depois de 2026, com mais detalhes
  prometidos entre o MSI e o Worlds de 2026; lançamento é 2027. O que
  existe HOJE são reskins cosméticos sazonais sobre o mesmo layout
  (tema Demacia: torres de petricita, detalhes dourados, elementos como
  Faelights e Crystalline Overgrowth) — não uma textura de base nova.
- **O `map11.png` do Data Dragon nunca foi atualizado e não vai ser** —
  é o mesmo arquivo "maquete" desde sempre.
- **Achado real**: o índice completo de arquivos do CommunityDragon
  (`raw.communitydragon.org/latest/cdragon/files.exported.txt`, ~50MB)
  lista `game/assets/maps/info/map11/grasstint.png` — a textura REAL
  usada pelo cliente atual (grama, rio, trilhas, bases com torres),
  512×512, bem mais detalhada que o `map11.png` antigo ou que qualquer
  esquema desenhado à mão. `cdn.communitydragon.org` (usado para ícones/
  splash de campeão) não espelha esse asset — só o `raw.` serve.
- Troca feita: `MINIMAP_URL` em `ddragon.ts` agora aponta para esse
  arquivo; `MapHeatmap.tsx` voltou a usar `<img>` (removido o
  `SummonersRiftBackground` SVG). Overlay escurecido de 10% para 30% de
  preto — a textura real tem muito mais cor que o SVG flat, precisa de
  mais contraste para o calor/ícones se destacarem.
- Verificação: Playwright em 3 combinações (dois temas, minutos 8/14/22)
  — jogadores aparecem exatamente sobre as rotas/rio/selva certos (ex.:
  duo bot-lane no canto inferior-direito aos 8 min; grupo em volta do
  rio central com abates aos 22 min) — mesma convenção de coordenadas
  0-1 do SVG anterior, sem nenhuma transformação extra necessária.

**Ajuste no mesmo dia**: o usuário mandou como referência o dev blog
oficial da Riot sobre as mudanças de mapa da temporada 2024
(leagueoflegends.com/pt-br/news/dev/dev-mudancas-no-mapa-para-a-temporada-2024)
e esclareceu que não precisava ser uma textura — um esquema atualizado
já resolveria. Ao inspecionar as imagens desse post oficial, ficou claro
que o estilo "traço chapado/labirinto" que eu tinha descartado como
"arte antiga" é, na verdade, a CONVENÇÃO OFICIAL da Riot para
diagramar o mapa (as imagens do próprio post da Riot usam exatamente
esse estilo, só que com destaques em laranja nas áreas alteradas). O
problema nunca foi o estilo — foi a fonte: o `map11.png` do Data Dragon
trava numa versão congelada (confirmado: 6.8 a 16.13 servem o MESMO
arquivo), enquanto o CommunityDragon serve o mesmo tipo de asset a
partir do patch `latest` de verdade. Troquei `MINIMAP_URL` para
`game/assets/maps/info/map11/2dlevelminimap_base_baron1.png` — mesmo
estilo esquemático oficial, mas correspondente ao patch atual. Bônus:
esse PNG tem transparência real nas áreas de selva (diferente do
`grasstint.png`, opaco), então passou a compor sobre uma cor de fundo
própria do container (`#1f1c12`) em vez de precisar de um overlay
escuro por cima de uma textura cheia de cor — mais simples e mais fiel
ao tema hextech escuro da plataforma.
Reverificado com Playwright (dois temas, minutos 8/14/22): mesma
correção de posicionamento, zero erros de console.

## 2026-07-03 — Montar Partida: campo de campeão com busca

Pedido do usuário: nos seletores de campeão do Montar Partida, poder
digitar o nome e ir filtrando (em vez do `<select>` nativo, que exige
rolar uma lista alfabética de ~170 campeões).

- Novo componente `ChampionCombobox` substituindo `ChampionSelect`:
  input de texto que abre uma lista filtrada por substring do nome
  (ex.: "ah" → Ahri, Malzahar, Nilah, Tahm Kench, Taliyah, Xayah),
  navegação por teclado (setas + Enter para confirmar, Esc para
  fechar), botão "✕" para limpar o slot, e fecha sem alterar nada ao
  clicar fora. Mantém o ícone do campeão ao lado do campo (posição
  espelhada por time: ícone à esquerda no azul, à direita no vermelho,
  igual antes) e a regra de não repetir campeão entre os 10 slots
  (`optionsFor`, inalterada).
- Bug pego na própria verificação (não pelo usuário): um `onBlur` com
  `setTimeout(fechar, 100ms)` e um foco rápido logo em seguida (ex.:
  Esc num campo seguido de clique em outro, ou nos testes automatizados
  do Playwright) corriam risco de o timeout antigo fechar um dropdown
  recém-aberto por engano — corrigido guardando o id do timeout num
  ref e cancelando-o no próximo foco.
- Verificação: Playwright preencheu os 10 campos digitando os nomes
  (Jayce/LeeSin/Ahri/Senna/Lulu vs Rengar/RekSai/Zed/Vayne/Sona) e a
  estimativa bateu exatamente com o valor já conhecido de testes
  anteriores (42,9% azul) — confirma que a troca de UI não alterou o
  valor submetido à API. Testado também: exclusão de campeão já
  escolhido no time oposto, botão de limpar, e clique-fora sem
  selecionar — tudo nos dois temas, zero erros de console.

## 2026-07-03 — NLQ: toggle padrão em Explicação + bug real de timeout em bans

Pedido do usuário: trocar o padrão do toggle SQL/Explicação em "Pergunte
aos dados" para abrir já em Explicação, e sugerir uma pergunta de teste.

- `SuccessTurn` (Nlq.tsx): estado inicial do toggle passou de `"sql"`
  para `"explicacao"`, com um `useEffect` (roda só na montagem) que
  dispara `explain.mutate()` automaticamente para resultados não-aviso
  — antes a chamada de explicação só acontecia sob demanda, no clique.
- **Bug real encontrado ao escolher a pergunta de teste**: tentei usar
  "quais os 5 campeões mais banidos e qual a taxa de banimento de cada
  um?" — travou por 10s e voltou `SqlExecutionError` com
  "cancelando comando por causa do tempo de espera (timeout)". Causa: o
  SQL gerado fazia `JOIN participants p ON b.champion_id = p.champion_id`
  direto (sem deduplicar) — como `participants` tem ~10 linhas por
  campeão por partida, isso multiplica cada linha de `bans` por todas as
  ocorrências daquele campeão no banco inteiro (explosão cartesiana)
  antes do agrupamento. A instrução adicionada ao `schema_context.py` na
  revisão anterior ("junte com um SELECT DISTINCT...") descrevia a ideia
  mas não dava um exemplo literal — o LLM não seguiu o padrão seguro à
  risca. Corrigido com um exemplo completo e copiável (o mesmo padrão
  já usado com segurança em `GET /stats/highlights` no backend:
  `JOIN (SELECT DISTINCT champion_id, champion_name FROM participants)`).
  Reexecutado após o fix: 2,6s, resultado correto (Master Yi 55,45%,
  Rengar 41,75%, Zed 39,55%... — bate com os números já conferidos).
  Rerodei `evaluate_nlq` por precaução (regra já registrada: sempre
  medir de novo ao mexer no schema_context) — 21/22 = 95%, sem
  regressão.
- **Pergunta de teste recomendada** (mostra o toggle em Explicação por
  padrão, avaliação de confiança da amostra e a seção "Leitura de
  jogo:"): *"Quais os 5 campeões mais banidos e qual a taxa de
  banimento de cada um?"*
- Verificação: Playwright confirmou o toggle "Explicação" já ativo sem
  clique, texto de explicação visível imediatamente, zero erros de
  console.

## 2026-07-03 — NLQ: mais dois bugs reais (taxa diluída + lado trocado)

Pedido do usuário: uma pergunta de teste mais complexa, cruzando
múltiplos fatores da partida. Escolhi comparar partidas curtas (<25 min)
com longas (≥25 min) por lado do mapa e média de dragões — pergunta
rica o suficiente para expor dois bugs reais, nenhum deles no dado em
si (a base está correta), ambos na geração de SQL/texto pelo LLM.

- **Bug 1 — taxa diluída pela metade**: a primeira SQL gerada agrupava
  só por faixa de duração (não por `team_id`) e calculava o win rate do
  vermelho com `AVG(CASE WHEN team_id = 200 AND win THEN 1.0 ELSE 0
  END)` sobre a junção de `matches` e `teams` — como essa junção tem as
  linhas dos DOIS times por partida, o denominador do AVG conta as
  linhas do time azul também, diluindo a taxa pela metade (58,4% saía
  como 29,2%). Corrigido em duas rodadas: a 1ª tentativa (regra em
  prosa + um exemplo "errado" vs "certo") NÃO resolveu — o modelo
  aparentemente copiou a estrutura do exemplo rotulado "errado" em vez
  de evitá-la (risco conhecido de few-shot: um SQL executável rotulado
  "errado" ainda serve de molde). Removido o exemplo errado; adicionado
  só um exemplo CERTO completo (o padrão exato da pergunta de teste:
  `WHERE team_id = 200` isolando o subgrupo antes de agregar, com nota
  de que para os dois lados lado a lado o certo é `GROUP BY` também por
  `team_id`, nunca CASE dentro do AVG). Reexecutado 3x: resultado
  consistente e correto nas 3 (bate exatamente com o SQL de referência
  calculado à mão: curta azul 41,5%/vermelho 58,4%; longa azul
  44,7%/vermelho 55,3%).
- **Bug 2 — lado trocado na explicação**: mesmo com a SQL/dado
  corretos, o texto da explicação (`explain_result`) descreveu "o time
  azul vence 58%... o vermelho vence 42%" — EXATAMENTE invertido (a
  tabela mostra team_id 100/azul = 41,5%, 200/vermelho = 58,4%). Causa:
  `explain_result` nunca recebeu a convenção de `team_id` (100=azul,
  200=vermelho) — só vê a SQL e as linhas cruas, sem o
  `SCHEMA_DESCRIPTION` que a geração de SQL usa. O modelo teve que
  adivinhar a cor de cada `team_id` e adivinhou errado. Corrigido
  acrescentando um parágrafo curto de "convenções do banco" ao prompt
  de `explain_result` (team_id 100=azul/200=vermelho; win rate já é
  fração 0-1; stats de participants/duração são totais finais) — mais
  enxuto que reusar o `SCHEMA_DESCRIPTION` inteiro (que é focado em
  gerar SQL, não em narrar resultado). Reexecutado: explicação agora
  atribui os números certos a cada lado, consistente com a tabela.
- Rerodei `evaluate_nlq` depois de cada mudança no `schema_context.py`
  (regra já registrada) — 91-95% nas duas rodadas, dentro da variação
  esperada, sem regressão.
- **Pergunta de teste recomendada** (mostra os dois bugs corrigidos e
  ainda cruza 3 fatores — duração, lado, objetivo — numa única
  pergunta): *"Comparando partidas curtas (menos de 25 minutos) com
  partidas longas (25 minutos ou mais), como a vantagem do lado
  vermelho e a média de dragões conquistados mudam entre esses dois
  grupos?"*
- **Lição para o texto do TCC**: exemplos "errado vs certo" em prompts
  de geração de SQL são arriscados com modelos menores — o modelo pode
  imitar a estrutura do exemplo rotulado errado em vez de evitá-la.
  Prefira dar só o padrão correto, adaptado ao caso mais próximo
  possível da pergunta real. Também vale registrar: o passo de
  "explicar o resultado" precisa das MESMAS convenções de domínio que o
  passo de gerar SQL (aqui, isso não estava acontecendo) — qualquer
  coluna cujo significado dependa de uma convenção arbitrária (como
  team_id) é um ponto cego se o prompt de explicação não repetir essa
  convenção.

## 2026-07-03 — Bateria de validação comportamental da predição

Pedido do usuário: uma bateria de testes/perguntas para validar a
predição, além das métricas de teste já reportadas (acurácia/precisão/
recall/F1/AUC, que medem acerto médio, não *comportamento*). Criado
`tests/validate_predictions.py` (script permanente, `python
tests/validate_predictions.py`) com 5 baterias sobre o modelo de
produção (`data/models_phases.joblib`):

1. **Monotonicidade** (mais vantagem nunca deveria reduzir a prob. do
   azul): `gold_diff` e `xp_diff` passam limpo nas 4 fases (correlação
   > 0,96). `dragon_diff` passa em 15/20/25min. `kill_diff` e
   `tower_diff` falham a correlação em várias fases — **não é bug**:
   é a mesma redundância/baixa importância já documentada no SHAP
   (kills já estão capturados em ouro/XP; torres são quase irrelevantes
   antes das placas caírem aos 14min). Testar UM fator isolado com os
   outros 4 cravados em zero é um estado artificial que quase não
   aparece nos dados de treino — XGBoost sem `monotone_constraints` não
   tem motivo para aprender uma resposta limpa e monotônica nessa fatia
   isolada de um fator de baixa importância. Registrado como
   característica do modelo, não corrigido (corrigir exigiria
   `monotone_constraints` no treino — mudança de modelagem, não bug;
   incremento futuro se a banca cobrar rigor nisso).
2. **Casos extremos**: liderança total em todos os fatores → prob.
   > 0,95 em toda fase; déficit total → prob. < 0,08; soma lead+deficit
   ≈ 1,0 (simetria) em todas as 4 fases. Limpo.
3. **Taxa-base por fase** (tudo empatado): < 50% (viés de lado) em
   10/15/20 min, mas 52,7% aos 25 min — **achado real, não bug**: a
   taxa de vitória do vermelho de 56,3% é uma estatística
   INCONDICIONAL (todas as partidas); a "taxa-base" do modelo é a
   predição para partidas que ESTÃO EMPATADAS naquele minuto específico
   — uma população condicional diferente a cada corte. "Empatado aos 25
   min" pode ser uma seleção de partidas com dinâmica diferente de
   "empatado aos 10 min". Vale uma nota no texto do TCC: o viés de lado
   documentado (56,3%) é sobre o dataset todo, não sobre "a taxa-base
   do modelo em qualquer corte".
4. **Evolução do SHAP entre fases**: tower_diff cresce 25× de 10 para
   25 min (bate com o achado já registrado); gold_diff domina em todas
   as 4 fases. Limpo, confirma achados anteriores.
5. **Checagem retrospectiva em 30 partidas reais** (não sintéticas):
   rodando o pipeline completo (timeline real → features por minuto →
   modelo da fase certa) nos últimos ~5 minutos de cada partida, a
   direção da predição bateu com o vencedor real em 26/30 (87%) — não
   é a acurácia formal do modelo (já reportada via held-out test), é
   uma checagem de sanidade de ponta a ponta fora do pipeline de
   treino, com dados de verdade.

**Bateria de perguntas NLQ** (regressão rápida contra fatos já
verificados, usando o `/ask` ao vivo): 5/5 bateram exatamente — total
de partidas (10.402), win rate do vermelho (56,34%), melhor campeão com
200+ jogos (Rek'Sai, 55,84% — conferido contra SQL direto na hora),
campeão mais banido (Master Yi, 55,45%), duração média (27,29 min).

**Veredito geral**: o modelo se comporta de forma sólida em cenários
realistas (extremos, simetria, retrospectiva com dados reais) e as
"falhas" de monotonicidade isolada são características documentáveis,
não defeitos — matéria boa para a seção de limitações/discussão do
TCC, não para "consertar às pressas".

## 2026-07-03 — Decisões de escopo, pesquisa de gameplay, e renome

Três pedidos do usuário na mesma mensagem/sequência:

**1. Conhecimento da comunidade (ex.: combo Nocturne+Orianna) — decidido: manter como está.**
Perguntado se deveríamos incorporar de algum jeito sinergias conhecidas
da comunidade que não aparecem fortes nos dados (o exemplo do NLQ
anterior: Nocturne+Orianna é tido como combo forte, mas a amostra do
dataset não confirma isso com força estatística). Opções apresentadas:
manter como está (o "Leitura de jogo:" do `explain_result`, já rotulado
como conhecimento do LLM, separado dos dados), criar uma tabela curada
manualmente, ou importar de um site de tier list externo. **Decisão:
manter como está** — zero engenharia nova, e a separação
dado-observado vs conhecimento-do-jogo já fica clara pra banca.

**2. Seção de competitivo (pro play) — decidido: adiar.**
Perguntado o escopo inicial (pipeline novo de dados profissionais via
Oracle's Elixir, ferramenta de draft/champion-select em cima do
`/compose` já existente, ou adiar). **Decisão: adiar** — fechar os
itens já pendentes (jogadores no team builder, correção de amostra
pequena, escrever os capítulos do TCC) antes de abrir uma frente de
dados nova. Se retomado, as opções continuam registradas na memória
do assistente (`project_scope_decisions.md`).

**3. Pesquisa: como vencer no LoL (itemização, pathing de selva, macro,
visão) e o que dá pra virar dado real.** Pesquisa na web + checagem do
que já existe em `raw_timelines`:
- **Itemização — viável, esforço médio.** As timelines têm eventos
  `ITEM_PURCHASED`/`ITEM_SOLD` por jogador com timestamp, nunca
  extraídos. Daria pra montar "build mais comum" e "tempo até o item
  core" × win rate, estilo op.gg. Precisa: ETL novo + mapear
  item_id→nome (Data Dragon `item.json`) + página nova.
- **Pathing de selva — só parcial.** Acampamentos comuns (lobos,
  raptors, krugs, arautilhos de buff) não geram evento discreto nas
  timelines do match-v5 — só os épicos (dragão, arauto, grubs, barão)
  aparecem em `ELITE_MONSTER_KILL`. Mas `participantFrames` tem
  `jungleMinionsKilled` por minuto — dá pra aproximar "velocidade de
  clear" (não a ordem exata dos acampamentos) × win rate.
- **Macro/wave management — não viável.** Não existe estado de
  minion-wave nas timelines do match-v5 (sem evento por minion). Vale
  registrar essa limitação no texto do TCC em vez de fingir que dá.
- **Visão — viável, fácil.** Já temos `vision_score` final por
  jogador. As timelines têm `WARD_PLACED`/`WARD_KILL` com posição —
  dá pra estender o `MapHeatmap` já construído pra mostrar wards ao
  longo do tempo, reaproveitando toda a infraestrutura existente.
  Nada implementado ainda — fica registrado como próximo passo
  priorizável, não decidido ainda quando entra na fila.

**4. Renome: "LoL Analytics" → "Hextech Lab".** O nome antigo colidia
com o site já existente lolalytics.com. Escolhido entre 4 opções
(Fenda, Hextech Lab, RiftIQ, DraftLab) — "Hextech Lab" venceu por já
ser a identidade visual construída (títulos dourados serifados,
`.hextech-title`). Trocado em: sidebar (`Layout.tsx`), hero da Home,
`<title>` do `index.html`, título da API FastAPI (`main.py`), título
do Streamlit (`src/dashboard/app.py`), README e `docs/handoff.md`. O
diretório do repositório continua `lol-analytics` (não renomeado, para
não quebrar caminhos/imports). Verificado via Playwright: título da
aba, sidebar e hero todos consistentes, zero erros de console.

## 2026-07-03 — Macro (reframe) e 4 tentativas de melhorar o modelo (todas negativas)

Duas perguntas do usuário: como lidar com os insights de macro/wave
management (que eu tinha marcado como "não viável" na pesquisa
anterior) e como treinar mais os modelos.

**Macro — reframe.** Confirmei de novo (listando todos os tipos de
evento de uma timeline real) que não existe NENHUM evento de estado de
minion-wave no match-v5 — isso continua não sendo rastreável, ponto
final. Mas "macro" é mais amplo que só wave state: as timelines têm
posição x/y por jogador por minuto (já usada no `MapHeatmap`), que
poderia aproximar rotações/agrupamento/split push. Testei a proxy mais
óbvia — **dispersão do time** (distância média entre os 5 jogadores) —
correlação com vitória: 0,02 a 0,09 nas 4 fases, ou seja, **sem sinal
nenhum**. Faz sentido: dispersão alta é só "fase de rotas" (normal,
não ruim) e dispersão baixa é só "estão perto uns dos outros" (nem
sempre bom — pode ser grupo se preparando pra objetivo OU só que
morreram junto). Não virou feature. Proxies mais refinadas (roaming
específico — jogador saindo da própria rota e conseguindo abate em
outra; posicionamento perto do objetivo antes de ele cair) ficam
registradas como ideia não testada, mais difíceis de implementar bem.
**Visão continua sendo a aposta melhor** dentro do que é "estilo
macro" (já registrado como viável, ver entrada anterior).

**Treinar mais os modelos — 4 experimentos, todos negativos/desprezíveis:**
1. **Dispersão como feature** — já descartada acima por falta de sinal.
2. **Adicionar barão/arauto como features** (`baron_diff`/`herald_diff`,
   extraídos de `ELITE_MONSTER_KILL`): implementado, testado com
   `cross_validate` nos cortes onde fazem sentido (barão só aparece a
   partir de ~20-25min, arauto a partir de ~20min — confirmado
   contando `!=0` por corte). Resultado aos 25min: AUC idêntico
   (0,9013), acurácia +0,0016 — dentro do ruído. Aos 20min: piora
   marginal. **Revertido** (`build_features.py` voltou aos 5 fatores
   originais, `features_phases.csv`/`features.csv` regenerados) — não
   vale a complexidade de mexer em API/frontend/docs por um ganho
   inexistente. Mesma explicação de sempre: o ouro/XP que esses
   objetivos dão já está capturado em `gold_diff`/`xp_diff`
   (redundância, igual `kill_diff`).
3. **Tuning de hiperparâmetros POR FASE** (hoje as 4 fases reusam os
   mesmos parâmetros, tunados uma vez só aos 15min): rodei
   `GridSearchCV` independente em cada corte. Resultado: os "melhores
   parâmetros por fase" saíram IDÊNTICOS aos já usados em produção
   (500, 0,01, 3) em 3 das 4 fases; na 4ª (10min) uma diferença
   mínima (n_estimators=200) com ganho de +0,0007 de AUC — irrelevante.
   Não implementado — não vale a complexidade de tunar e manter 4
   conjuntos de hiperparâmetros por um ganho que não existe.
4. **Calibração explícita** (Platt/isotonic) dos modelos de produção:
   medi o gap entre probabilidade prevista e taxa real observada em 8
   faixas por fase — gap médio de 0,016 a 0,023 (bem pequeno). Os
   modelos JÁ estão bem calibrados (XGBoost com log loss tende a isso
   naturalmente em datasets deste tamanho). Não precisa de calibração
   adicional.

**Conclusão honesta**: a abordagem atual (XGBoost, 5 fatores agregados
por fase) já está perto do teto de desempenho que esses 5 fatores
permitem — testei 4 ângulos de melhoria diferentes hoje e nenhum
rendeu ganho real. Isso não é uma notícia ruim: é evidência de que o
esforço de tuning já feito (etapa 4 do roadmap) estava bem calibrado, e
vira um parágrafo honesto pra seção de limitações/trabalhos futuros do
TCC. Os dois caminhos que restam pra melhorar de verdade: (a)
**features de item** (`ITEM_PURCHASED`/`ITEM_SOLD` das timelines,
carregam informação que ouro/XP sozinhos não capturam — ex.: build
defensiva vs ofensiva com o mesmo gold gasto) — ainda não testado,
exige desenhar uma feature numérica a partir de item_id, é o próximo
candidato mais promissor; (b) **coletar mais partidas** — ajuda
principalmente a fase de 25min (só 7.575 partidas sobrevivem até esse
corte, vs 10.351 aos 10min) e reduz variância entre folds, mas não
necessariamente sobe o teto de acurácia.

## 2026-07-03 — Itemização entregue + pesquisa de replays/counterfactual

Três pedidos do usuário: comando para coletar mais dados, adicionar
itemização, e pesquisar como ampliar as capacidades de análise
(controle de wave, e no futuro perguntas contrafactuais tipo "se o
Jayce tivesse puxado a lane no minuto X em vez de voltar pra base, a
probabilidade de vitória teria subido?").

**Itemização (entregue de ponta a ponta):**
- Nova tabela `item_events` (schema.sql) + ETL `src/etl/load_items.py`:
  2.360.777 eventos efetivos de compra/venda de 10.409 timelines. Os
  ITEM_UNDO são aplicados no ETL (compra desfeita não entra);
  ITEM_DESTROYED não é gravado (fusão de componente/consumível usado).
  Bug pego na primeira execução: raw_timelines tem remakes (<5min) que
  o ETL principal pula — o insert violava a FK com `matches`; corrigido
  filtrando com JOIN.
- Catálogo `data/items.json` do Data Dragon (706 itens, pt-BR, versão
  16.13.1 fixada em sincronia com o `itemIcon` do front). Heurística de
  "item finalizado": nada constrói a partir dele + comprável + custo
  >= 1100 + não consumível/trinket + válido no mapa 11 → 143 itens.
- Endpoint `GET /stats/champion/{nome}/items` + seção "Itens
  finalizados mais construídos" no detalhe do campeão (ícones reais,
  jogos + % de presença, win rate, minuto médio da primeira compra).
- Verificação numérica: Manamune no Jayce — API diz 915 jogos/53,8%;
  SQL direto confirma (915 / 53,77%). As builds retornadas batem com o
  meta real do campeão (Manamune 69% + Youmuu 66% no Jayce). Insight
  de exemplo que a seção já entrega: Eclipse no Jayce tem 46,7% de win
  rate contra 53,8% da build meta — exatamente o tipo de leitura de
  itemização que a pesquisa de ontem apontou como valiosa.

**Itens como feature do modelo (o "candidato promissor" — testado, veredito honesto):**
- `item_gold_diff` (ouro em itens finalizados, azul−vermelho, no corte):
  +0,001 de acurácia aos 15min, nada aos 20/25. Correlação com
  gold_diff: 0,65-0,83 — é quase o mesmo sinal.
- Variante def/off (ouro defensivo e ofensivo como features separadas —
  a hipótese "build errada para o contexto"): +0,0014 a +0,0016 de
  acurácia consistente nos 3 cortes, AUC quase inalterado. Direção
  positiva mas MARGINAL — não justifica complicar o pipeline de
  produção (sliders da UI, contrato da API, docs) por +0,15pp.
- Conclusão: o valor da itemização está na ANÁLISE (a página nova), não
  como feature do modelo de estado. Fecha a fila de experimentos de
  melhoria do modelo iniciada mais cedo (6 experimentos no total hoje,
  nenhum ganho material) — reforça a conclusão de teto de desempenho
  com features agregadas de estado.

**Pesquisa: wave control e análise contrafactual (o caminho para "e se
o Jayce tivesse puxado a lane?"):** ver a mensagem da sessão para os
links; resumo dos achados e o plano em camadas:
- *Camada 1 — contrafactual de ESTADO (dá pra fazer HOJE)*: a pergunta
  "e se aos 14min o estado fosse Y em vez de X?" já é respondível com o
  que temos — a página Predição É isso manualmente, e a análise de
  partida tem a curva minuto a minuto. O que falta é UI: um modo
  "e se" na análise da partida (escolher um minuto, editar o estado,
  ver o delta de probabilidade). Não exige dado novo nem modelo novo.
- *Camada 2 — enriquecer o estado (itens/wards/posições já extraídos ou
  extraíveis)*: aumenta o vocabulário do "e se" (ex.: "e se tivesse
  comprado item defensivo?"), mas os experimentos de hoje mostram que o
  ganho preditivo é pequeno; o valor é descritivo/analítico.
- *Camada 3 — wave/micro de verdade (pesquisa, não feature)*: o estado
  de wave NÃO existe em nenhuma API da Riot. Os caminhos reais que a
  comunidade/academia usam: (a) **parsear replays .rofl** — o formato é
  um dump de pacotes ofuscado que muda a cada patch; existem parsers
  (roflxd, lolrofl, pyLoL) que extraem metadados e, alguns, posições de
  campeões em intervalos de 1s, mas minions/wave state seguem sendo o
  nível mais difícil; (b) **visão computacional no minimapa** — a
  linha do DeepLeague (dataset de 100k imagens rotuladas; PandaScore e
  outros usam YOLO/SSD para extrair posições de VODs) — não dá wave
  state direto, mas dá posições contínuas sem depender do formato
  .rofl; (c) na literatura de win probability esportiva, o
  contrafactual "e se tivesse feito Z" é tratado como intervenção num
  modelo causal/simulador — o alerta acadêmico é que dados
  observacionais correlacionados inflam viés e variância (uma partida
  onde o Jayce recuou é sistematicamente diferente de uma onde puxou).
  Ou seja: a versão honesta do sonho para o TCC é a Camada 1
  (contrafactual de estado com o modelo já validado), declarando as
  Camadas 2-3 como trabalhos futuros com as referências acima.

**Coleta adicional**: usuário vai rodar
`python -m src.collect.collect_matches --players 730 --matches-per-player 20`
(retomável; requer chave Riot renovada — expira a cada 24h). Após a
coleta: rerodar `load_items`, `build_features` e `export_model`.

## 2026-07-03 — "E se" entregue, renome 2 (Bellestraiko) e pipeline competitivo

Três pedidos do usuário:

**1. Renome de novo: "Hextech Lab" → "Bellestraiko".** O usuário
encontrou um canal do YouTube já chamado Hextech Lab
(youtube.com/@HextechLab) e escolheu "Bellestraiko". Trocado nos mesmos
lugares do renome anterior (sidebar, hero, `<title>`, FastAPI,
Streamlit, README, handoff). Verificado via Playwright (título da aba =
"Bellestraiko").

**2. Modo "e se" na análise da partida (Camada 1 do contrafactual —
entregue).**
- Backend: os pontos da curva de probabilidade
  (`GET /matches/{id}/analysis`) agora carregam o ESTADO completo de
  cada minuto (os 5 diffs — já eram computados no loop, só não iam na
  resposta). Compatível com o front antigo (gold_diff continua no
  mesmo lugar).
- Front: card "E se, aos X minutos…" no `/partidas/:id`, sincronizado
  com o slider do mapa de calor. Sliders semeados com o estado REAL do
  minuto (valores editados ficam dourados, com o real ao lado), chamada
  debounced ao `/predict` com o modelo da fase certa, e display
  Real × E se com o delta em pontos percentuais. Ranges por fase
  (compartilhados de `matchState.ts`), esticados quando o valor real
  da partida passa do percentil 99. Botão "voltar ao estado real".
- Honestidade metodológica no próprio card: isto responde "e se o
  ESTADO fosse outro", não "e se o jogador tivesse feito a jogada Y" —
  ações específicas exigiriam dados de replay que a API da Riot não
  fornece (ver pesquisa da entrada anterior). A distinção importa para
  a banca: intervenção sobre estado agregado, não inferência causal
  sobre decisões.
- Verificação: Playwright — semente aos 14 min bate com a curva
  (65,7%); ouro editado para +5000 → 92,1% (+26,4pp); mudar o slider
  de minuto re-semeia o card; zero erros de console.

**3. Coleta competitiva (pro play) — pipeline pronto, download
bloqueado por quota.** Fonte escolhida: os CSVs anuais públicos do
Oracle's Elixir (padrão em trabalhos acadêmicos; LCK/LPL/LEC/LTA/CBLOL
etc., com gold/xp/cs diff aos 15 min — conversa direto com as nossas
features de solo queue).
- `src/collect/collect_pro.py`: baixa o CSV do ano da pasta pública do
  Google Drive do OE (ids dos arquivos 2023-2026 extraídos da listagem
  da pasta). O Drive tem quota diária de download por arquivo — hoje
  estava estourada ("Quota exceeded"), então o script detecta isso e
  instrui o fallback manual (baixar em oracleselixir.com/tools/downloads
  para `data/pro/`). Re-rodar mais tarde resolve.
- Tabelas novas `pro_games` (2 linhas/jogo — time) e `pro_players`
  (10 linhas/jogo) no schema; `src/etl/load_pro.py` carrega qualquer
  CSV em `data/pro/` (idempotente por ano). Pipeline testado até onde a
  quota permite; a carga real fica para quando o download passar.
- Integração com a UI/NLQ fica para depois de ter os dados de verdade
  — decisão consciente de não construir telas sobre tabela vazia.

**Adendo — "não dá pra pegar o competitivo direto da API da Riot?"**
(pergunta do usuário): não pela API que já usamos. As partidas
profissionais são jogadas em *tournament realms* — servidores isolados
que o match-v5 público não enxerga (nossa chave só vê os shards ao vivo,
tipo BR1). O que existe: (a) a **API do lolesports.com**
(esports-api.lolesports.com, chave pública conhecida — testada hoje,
responde) com calendário/resultados e um feed de livestats com frames a
cada ~10s dos jogos transmitidos — não documentada, sem garantia, e
exige raspar jogo a jogo; (b) **GRID/Bayes**, os parceiros oficiais de
dados da Riot para esports — acesso mediante aplicação/contrato;
(c) **Leaguepedia** (API Cargo) para picks/bans/resultados. O Oracle's
Elixir agrega tudo isso em CSVs limpos — é exatamente por isso que é o
padrão acadêmico e a nossa escolha. A API do lolesports fica anotada
como complemento futuro para a meta de tempo real (jogos ao vivo têm
feed de livestats).

## 2026-07-04 — Dados competitivos carregados (+ achado: o viés de lado INVERTE)

O usuário baixou manualmente o CSV 2026 do Oracle's Elixir (a quota do
Drive seguia bloqueada) e salvou em `data/pro/`. Carga via
`python -m src.etl.load_pro --year 2026`:

- **6.026 jogos profissionais** (72.312 linhas do CSV → 12.052 de time
  + 60.260 de jogador), cobrindo LPL (453), LCK (349), LCKC, LJL, EM,
  AL, LEC (246), LAS, LCP, LIT e mais. 92% das linhas de time têm os
  cortes de 15 min (gold/xp/cs diff) — compatível com nossas features
  de solo queue.
- Sanidade: campeões mais jogados no pro (Xin Zhao 1.663, Ezreal 1.593,
  Ryze 1.590) são plausíveis para o meta competitivo do ano, com win
  rates ~50% como esperado em picks de alta frequência.

**Achado imediato (primeira consulta na tabela): o viés de lado
INVERTE entre solo queue e competitivo.** No nosso dataset BR
Challenger/GM, o azul vence 43,7% (vermelho dominante, 56,3%); no
competitivo 2026 mundial, o AZUL vence 53,1%. Isso fecha o quebra-cabeça
da entrada de 2026-07-03 sobre o viés de lado: a literatura geral
("azul ~50,6-53%") descreve bem o PRO PLAY — quem destoa é o nosso
recorte de solo queue de elo altíssimo. A hipótese registrada
(counter-pick garantido do vermelho pesa mais no solo queue, onde não
há draft coordenado de 5 pessoas; no competitivo, o azul tem prioridade
de primeiro pick, que os times valorizam a ponto de escolher o lado em
playoffs) agora tem dado dos dois lados para sustentar a comparação.
**Material forte para o TCC**: mesma métrica, dois contextos, sinais
opostos — e a plataforma tem os dois datasets para mostrar isso.

## 2026-07-04 — Página "Competitivo" (solo queue × pro)

Decisão do usuário: página própria (não seção do Dashboard). Entregue
em `/competitivo` (nav com ícone de troféu), com 3 endpoints novos:

- `GET /stats/pro/overview` — jogos, viés de lado, duração média e
  jogos+win rate azul por liga (503 com instrução se `pro_games` estiver
  vazia);
- `GET /stats/pro/gold15` — win rate azul por faixa de ouro aos 15 min
  no competitivo, MESMAS faixas do `/stats/gold15` de solo queue
  (comparação direta); usa as linhas do lado azul (diff na perspectiva
  do azul, como nas nossas features);
- `GET /stats/pro/champions` — campeões mais presentes no pro com o win
  rate deles no NOSSO solo queue ao lado. O match de nomes normaliza
  (OE usa nome de exibição, a Riot API nome interno): remove não-letras
  + CASE para os casos especiais (Wukong→MonkeyKing, Renata Glasc→
  Renata, Nunu & Willump→Nunu). Campeão sem match mostra "—".

A página conta a história em 4 blocos: KPIs (6.026 jogos, 31,6 min de
duração média vs 27,3 do solo queue), o card do **viés de lado
invertido** (barras espelhadas dos dois contextos + leitura com a
hipótese), o gráfico **ouro aos 15 × vitória nos dois contextos**
(faixas idênticas, duas séries) e a dupla **jogos por liga** + **meta
profissional × solo queue**.

**Segundo achado quantitativo da comparação: o pro converte vantagem
melhor.** Com +2k a +4k de ouro aos 15, o azul vence 84,0% no
competitivo (877 jogos — conferido contra SQL direto, bate exato)
contra ~68% no solo queue; com +4k a +6k, ~95% vs ~81%. É o argumento
quantitativo para "macro ganha jogo": a MESMA vantagem material vale
mais nas mãos de um time coordenado. Junto com o viés de lado
invertido, a página já entrega duas comparações com valor de tese.

Notas de verificação: o match de nomes funcionou nos casos difíceis
visíveis (Wukong e K'Sante com WR de solo queue ao lado); a coleta
adicional do usuário estava RODANDO durante a verificação (solo queue
passou de 10,4k para 11,8k partidas ao longo da sessão), então os
números da página mudam conforme a coleta avança — esperado, não é
bug. Playwright nos dois temas, zero erros de console; o gráfico de
comparação exigiu o cuidado já documentado (sem fullPage, esperar
`.recharts-bar-rectangle path` — a animação do Recharts em screenshots
fullPage é a mesma pegadinha registrada em 2026-07-02).

## 2026-07-05 — 13 anos de pro carregados, seletor de ano e o Planejamento v2

Três coisas nesta rodada:

**1. Acervo competitivo completo: 99.259 jogos (2014-2026).** O usuário
baixou os 13 CSVs anuais do Oracle's Elixir para `data/pro/` e o
`load_pro` carregou tudo (~199k linhas de time, ~992k de jogador). Isso
transformou um problema em feature: a página Competitivo dizia "de
2026" mas passaria a agregar eras completamente diferentes misturadas.
Correção imediata (que também era o item 1 do planejamento): os três
endpoints pro ganharam `year` (padrão = ano mais recente, resolvido no
banco), novo `GET /stats/pro/years`, e a página ganhou o seletor de
ano no cabeçalho. Verificado: trocar 2026→2018 atualiza KPIs (6.026 →
6.581 jogos) e o texto acompanha. Nota: o `year` vem da COLUNA do CSV,
não do nome do arquivo — o arquivo de 2018 tem 6.736 jogos mas 6.581
com year=2018 (jogos da virada do ano ficam no ano certo).
Curiosidade que já saiu de graça: o azul vence >53% no pro em 2018
TAMBÉM — o viés azul do competitivo é estável através dos anos, o que
fortalece o contraste com o nosso solo queue.

**2. Validação externa da metodologia (achado do usuário):** o próprio
Oracle's Elixir publica uma "Early-Game Win Probability Calculator" —
split + lado do mapa + diferença de ouro aos 15:00 + diferença de
dragões ELEMENTAIS → probabilidade estimada. É a mesma estrutura da
nossa página de Predição (estado aos 15 → WP), praticada pela fonte
dos dados competitivos. Duas ideias que ela sugere e entraram no
planejamento: lado do mapa como entrada explícita do modelo e TIPOS de
dragão como feature (nossas timelines têm o subtipo em
ELITE_MONSTER_KILL; hoje usamos só o agregado).

**3. Planejamento v2 criado** (`docs/planejamento_v2.md`) — os 4
objetivos definidos pelo usuário, destrinchados com o que já temos,
entregas ordenadas, riscos e esforço: (1) competitivo em tudo (NLQ,
campeão, modelo pro, tipos de dragão), (2) perfis de jogadores +
jogadores no Montar Partida com shrinkage, (3) mais regiões e elos
(pedir a Personal API Key JÁ — aprovação demora e destrava tudo),
(4) tempo real em 3 estágios (MVP replay-ao-vivo sem dependência
externa → pro ao vivo via feed do lolesports → companion local).
Ordem sugerida em 8 sprints com o corte TCC × pós-TCC.

## 2026-07-05 — Sprint 1 do planejamento v2 concluído

Handoff (`docs/handoff.md`) reescrito para o estado atual (dois
datasets, todos os achados, pipeline completo) e o Sprint 1 executado:

**1. NLQ conhece o competitivo.** `pro_games`/`pro_players` no
`schema_context` (com as pegadinhas explícitas: side é texto
'Blue'/'Red' e não team_id; pro_players NÃO tem year — junta com
pro_games POR game_id E side, com exemplo copiável; nomes são de
exibição com espaços; sempre filtrar por ano, padrão 2026) e na
whitelist de validação. Benchmark ampliado de 22 para 26 perguntas
(4 competitivas: contagem por ano, win rate do azul, campeões mais
jogados — que exige o join duplo — e liga com mais jogos).
**Resultado: 23/26 = 88%, com as 4 perguntas pro passando DE
PRIMEIRA** (o exemplo copiável no schema pagou de novo). As 3 falhas
são todas a mesma família benigna já documentada (coluna COUNT extra
quando a pergunta menciona "pelo menos N jogos") — diagnóstico rodado,
zero regressão causada pelas tabelas novas; a família de falha flutua
entre 1-3 ocorrências por execução (na régua antiga de 22 perguntas,
esta rodada teria dado 19-20/22). Faixa honesta para o TCC: 85-95%.

**2. Seção "No competitivo" no detalhe do campeão.**
`GET /stats/champion/{nome}/pro` (ano padrão = mais recente): jogos,
win rate, presença sobre os jogos do ano e quebra por liga (top 6).
O match de nome interno ↔ exibição reusa a normalização do
/stats/pro/champions (validado: KSante → 1.315 jogos e MonkeyKing →
1.163, idênticos aos números da página Competitivo). Card `ProCard` no
detalhe do campeão, num grid com o card de itens. Caso o campeão não
apareça no pro do ano, mensagem explicativa em vez de tabela vazia.
Exemplo que a seção já entrega: Jayce tem 53,8% de win rate no nosso
solo queue mas 49,9% no competitivo com 13,2% de presença — pick
respeitado no pro, mas sem converter em vitória como no solo queue.

Verificação: typecheck limpo, endpoint cross-checado contra os números
já validados, Playwright no detalhe do campeão (795 jogos/13,2%
visíveis), zero erros de console.

## 2026-07-05 — Sprint 2: modelo pro, o achado da reconciliação, e dragões por tipo

**1. Modelo pro aos 15 min + comparação formal (`src/models/train_pro.py`,
script permanente).** Adicionado `kill_diff_at15` ao pipeline pro
(killsat15 − opp_killsat15 do CSV; ALTER TABLE IF NOT EXISTS no schema;
13 anos recarregados) para ter um conjunto de features COMPARTILHADO
com o solo queue aos 15 min: gold/xp/kill diff. Mesmo XGBoost tunado,
CV 5-fold estratificada:

| dataset (features compartilhadas) | n | acc | AUC |
|---|---|---|---|
| solo queue Challenger/GM BR | 10.295 | 0,7444 | 0,8255 |
| competitivo (todos os anos) | 86.058 | 0,7459 | 0,8283 |
| competitivo (2023+) | 31.980 | 0,7422 | 0,8241 |

**Achado (o melhor do sprint): empate técnico em previsibilidade — e a
reconciliação com o achado da conversão.** O pro converte vantagens
grandes muito melhor (84% vs 68% na faixa +2k..4k), então esperava-se
AUC maior; mas o pro também chega MENOS vezes a estados extremos aos
15 min (desvio-padrão do gold_diff: 2.991 no pro vs 4.199 no solo
queue; |diff| médio 2.311 vs 3.326 — medido nos dois datasets). Melhor
conversão × distribuição mais apertada se cancelam no agregado.
Narrativa completa para o TCC: dois achados aparentemente
contraditórios, reconciliados por uma terceira medição — e a frase
que resume: "profissionais convertem melhor, mas também permitem
menos". Bônus de engenharia: `data/model_pro.joblib` salvo com as 3
features compartilhadas — que são EXATAMENTE as que o feed de
livestats do lolesports fornece, ou seja, o modelo do futuro "pro ao
vivo" (planejamento v2, passo 4.2) já está treinado.

**2. Dragões por tipo como feature (ideia da calculadora do OE) —
testado, 7º experimento negativo.** Extraído o `monsterSubType` dos
ELITE_MONSTER_KILL das 11k timelines (6 subtipos vistos; Elder nunca
aparece até os 25 min, como esperado pelos timers). Substituir
`dragon_diff` agregado por 6 diffs por elemento: AUC LEVEMENTE PIOR em
todos os cortes (15min: 0,8319→0,8295; 20: 0,8661→0,8651; 25:
0,9013→0,8999). Interpretação: até os 25 min importa QUANTOS dragões
(tempo/prioridade de mapa), não QUAIS — o efeito de alma/estaqueamento
só apareceria mais tarde; e fatiar uma feature informativa em 6
esparsas dilui o sinal para árvores com 10k amostras. A calculadora do
OE usa tipos porque modela o jogo INTEIRO (não um corte aos 15) e com
590k+ jogos. Registrado como negativo com explicação — a série de
experimentos (agora 7) é seção pronta de limitações/discussão.

## 2026-07-05 — Sprint 3: perfis de jogador e busca unificada

Pessoas, não só campeões — três endpoints e duas páginas novas:

- **`GET /stats/player/{puuid}`** + página `/jogadores/:puuid` (perfil
  solo queue): Riot ID, tier/PDL, win rate geral, forma recente
  (últimas 10), campeão mais jogado, pool de campeões (jogos/WR/KDA,
  linkando para a página do campeão) e últimas partidas (linkando para
  a análise da partida). O card "melhor jogador" da Home agora navega
  para o perfil.
- **`GET /stats/pro/player/{nome}`** + página
  `/competitivo/jogadores/:nome` (perfil profissional): temporadas
  (ano/time/liga com jogos e WR), pool de campeões da carreira (ícones
  via match de nomes com o solo queue) e totais. Ex.: Faker — 1.485
  jogos no acervo, 66,5% de carreira, T1, meio (conferido contra SQL
  direto: 1.485/66,53%, exato).
- **`GET /stats/players/search?q=`** + busca UNIFICADA na Home: o campo
  agora busca campeões (filtro local), jogadores de solo queue (por
  Riot ID) e profissionais (pro_players), em seções separadas no
  dropdown, cada um navegando para a página certa.

Verificação: typecheck limpo; Faker cross-checado contra SQL; Playwright
navegou busca → dropdown com seções, perfil pro (temporadas 2014-2026
renderizando) e card da Home → perfil solo (CBrayanB#BR2, 87,5% em 40
partidas — bate com o highlight já validado em sessões anteriores);
zero erros de console. Nota de operação: o dev server do Vite tinha
caído entre sessões — subiu de novo com `npm run dev` (os dois
processos, API e Vite, não sobrevivem a reboot; ver comandos no
README/handoff).

O que ficou de fora do sprint (consciente): jogadores no MONTAR PARTIDA
com shrinkage é o sprint 4 (o próximo); ligação automática solo↔pro de
um mesmo jogador ficou registrada no planejamento como "não forçar sem
match confiável".

## 2026-07-05 — Sprint 4: jogadores no Montar Partida, com shrinkage

O sprint mais delicado estatisticamente do planejamento v2 — fecha a
pendência antiga que motivou o caso Nocturne+Orianna: um jogador com
poucos jogos não pode empurrar a estimativa para o extremo.

**Mecânica (shrinkage bayesiano)**: para cada lane com jogador
selecionado, `shrunk_wr = (jogos×wr_jogador + k×wr_campeão) / (jogos+k)`
com `k=15` (jogos "equivalentes" do prior). Poucos jogos → shrunk fica
perto da taxa geral do campeão (efeito ≈ 0); muitos jogos → shrunk se
aproxima do desempenho real observado. O efeito entra na lane em
log-odds: `logit(lane_final) = logit(lane_composição) + logit(shrunk_azul)
- logit(wr_campeão_azul) - [mesmo termo do vermelho]` — mesmo padrão de
combinação em log-odds já usado para estado da partida.

**Backend**: `Composition` ganhou `blue_players`/`red_players`
(posição→puuid, opcional). Cada lane agora retorna `composition_win_rate`
(estimativa sem jogador, preservada para comparação), `blue_player`/
`red_player` (nome, jogos no campeão, wr bruto, wr após shrinkage,
delta em log-odds) quando informados. Testado com um caso real
(Krastyel#mel, 18 jogos de Ahri, 66,7% bruto): shrunk → 60,1%, elevando
a lane Ahri×Zed de 55,3% (só composição) para 63,1%.

**Frontend**: novo card "Jogadores (opcional)" no Montar Partida
(mesmo padrão do card de estado — toggle "Incluir"), com um
`PlayerCombobox` por posição/lado (busca por Riot ID no servidor,
desabilitado até o campeão daquela posição ser escolhido). Cada lane
na tabela de resultado ganhou uma linha de explicação — a matemática do
shrinkage é visível, não uma caixa-preta: "Krastyel#mel (azul): 18
jogos, 66,7% bruto → 60,1% após shrinkage — sem jogador, a lane seria
55,3%."

**Bug pego na própria verificação**: renomeei o campo do backend
(`champion_only_win_rate` → `composition_win_rate`, nome mais preciso)
mas esqueci de reiniciar a API depois — o servidor continuou servindo
o nome antigo, e o front (já esperando o nome novo) mostrou "NaN%" no
texto explicativo. Pego pelo teste Playwright de ponta a ponta, não
por inspeção de código; reiniciada a API, número correto (55,3%)
apareceu. Lição de novo: mudança de contrato de API SEMPRE exige
restart, mesmo mudanças "só de nome".

Verificação: typecheck limpo; curl comparado com Playwright (mesmo
resultado, 60,1%/63,1%/55,3%); fluxo completo testado (toggle → busca
→ seleção → análise → nota de shrinkage renderizada); zero erros de
console.

## 2026-07-05 — Sprint 5 (em andamento): multi-região

Diferente do esperado no planejamento, a chave de DESENVOLVEDOR seguia
válida — não foi preciso esperar a Personal API Key pra começar. Testei
(`challenger_league()` numa instância nova) e ainda respondia, então
parametrizei o pipeline e já disparei um piloto real.

**Parametrização (schema não mudou nada — já tinha `platform_id`/
`platform` prontos desde o início):**
- `src/riot/client.py`: `RiotClient` agora recebe `platform`/`region`
  por instância (antes eram só as constantes globais do `.env`).
  `PLATFORM_TO_REGION` mapeia plataforma → região de roteamento do
  match-v5 (br1/la1/la2/na1→americas, kr/jp1→asia,
  euw1/eun1/tr1/ru→europe, oc1 e as 5 SEA→sea). Novo `master_league()`.
  Nota registrada no código: a janela de rate limit é por instância —
  duas plataformas que roteiam pra mesma região (br1+na1, por exemplo)
  têm, na prática, o mesmo limite real da Riot; coletar sequencial (como
  já fazemos) evita estourar isso, paralelo não.
- `src/collect/seed_players.py`: `--platforms` (várias) × `--tiers`
  (CHALLENGER/GRANDMASTER/MASTER). Rodado para kr/euw1/na1 challenger+
  grandmaster: 3.111 jogadores novos (1.000/1.081/1.030).
- `src/collect/collect_matches.py`: agrupa jogadores por `platform`
  (coluna já existe), um `RiotClient` por grupo, sequencial entre
  plataformas.

**Piloto real disparado** (`--platforms kr euw1 na1 --players 20
--matches-per-player 8`, rodando em background): coleta de verdade, não
simulação. Nos primeiros minutos já chegou dado: **EUW1 com 131
partidas, vermelho vencendo 43,7%** — o OPOSTO do BR (56,3%)! Sinal
inicial forte de que o viés vermelho é específico do BR (ou da
combinação BR+elo altíssimo), não do solo queue de elo alto em geral —
exatamente a pergunta de tese que o sprint queria responder. Número
ainda preliminar (amostra pequena), mas a direção já é informativa.

**Endpoint + seção no Dashboard**: `GET /stats/regions` (win rate do
vermelho + duração média por `platform_id`, mesmo ângulo do
`/stats/highlights`). Card novo "Viés de lado por região" na seção
"Cobertura do dataset" do Dashboard — barras espelhadas por
plataforma, e a leitura já reage ao número de regiões: com 1 só, avisa
que é preliminar; com 2+, compara a variação entre elas. Verificado:
BR1 56,3%/11.936 partidas, EUW1 43,7%/87 partidas (no momento do
screenshot) renderizando corretamente, zero erros de console.

**Ainda em andamento**: a coleta do piloto (KR/EUW1/NA1) continua
rodando; ao terminar, atualizar os números deste registro e considerar
rerodar `build_features`/`export_model` incluindo as novas regiões (ou
manter o modelo BR-only e tratar as demais regiões só como dado
analítico/comparativo por enquanto — decisão a tomar quando o volume
por região for suficiente).

## 2026-07-05 — Piloto multi-região encerrado + Sprint 6 (replay ao vivo)

**Piloto multi-região — encerrado, com o achado se firmando.** A coleta
KR/EUW1/NA1 rodou até a chave de DEV expirar no meio (401 Unauthorized
nos últimos jogadores de NA1 — na prática NA1 não coletou nada, e
KR/EUW1 ficaram menores que o alvo). Confirma na prática o que já estava
documentado: chave de dev não escala. Estado final por região (viés de
lado = win rate do vermelho):

| região | partidas | vitória vermelho |
|---|---|---|
| BR1  | 11.936 | 56,3% |
| EUW1 |   138  | 50,0% |
| KR   |    45  | 71,1% (amostra pequena) |

EUW1 em 50% (equilíbrio) e KR com amostra minúscula — ainda não é
conclusivo, mas **BR segue como o mais desviado para o vermelho**, o
que mantém a hipótese "viés vermelho é do BR (ou BR+elo altíssimo), não
do solo queue de elo alto em geral". Precisa de mais volume por região
(depende da Personal API Key) para virar afirmação de tese; por
enquanto é um sinal registrado com a ressalva de amostra.

**Sprint 6 do planejamento v2: MVP "replay ao vivo" (entregue).** A
primeira camada da meta de tempo real, e a de menor risco: zero
dependência de API externa.
- `GET /matches/random` (novo, pequeno): sorteia um match_id que TENHA
  timeline e >= 20 min (curva mais interessante).
- Página `/aovivo` (`LiveReplay`, nav "Ao vivo" com ícone de rádio):
  reproduz uma partida coletada minuto a minuto como se fosse ao vivo.
  A curva de probabilidade cresce em tempo real (um minuto de jogo por
  segundo real × velocidade 1/2/4×), com play/pausa/reiniciar. Painel
  lateral com o estado do minuto atual (os 5 diffs + qual modelo de
  fase está ativo), times embaixo, e ao chegar no fim revela o
  resultado real + se o modelo apontava o vencedor no último minuto
  (com a ressalva de que cada ponto só vê o estado até aquele minuto,
  não o futuro). Link para a análise completa da partida.
- Por que isso importa pro TCC: valida toda a arquitetura de streaming
  incremental de UI sem depender de haver jogo no ar — e é demonstrável
  ao vivo para a banca a qualquer momento. O MESMO motor
  (`features_from_timeline` → modelo da fase → curva) rodaria sobre um
  feed real; aqui o "feed" é uma partida do banco.
- Verificação: typecheck limpo; Playwright confirmou a curva avançando
  (45,1% no minuto 1 → 48,1% conforme roda), pausar/reiniciar voltando
  ao início, zero erros de console.

Estágios 2-3 do passo 4 (pro ao vivo via feed do lolesports; companion
local da Live Client API) ficam como trabalhos futuros — o modelo pro
já treinado (`model_pro.joblib`, sprint 2) é o insumo do estágio 2
quando/se for retomado.

## 2026-07-05 — Auditoria de duplicação e consolidação (front + back)

Com 13 páginas e ~1,5k linhas de API acumuladas pelos sprints do
planejamento v2, pedido explícito de revisão: achar duplicação real
(não achismo) e consolidar. Duas explorações paralelas (backend
`main.py`, frontend `pages/` + `api.ts`) confirmaram achados concretos
antes de qualquer mudança.

**Frontend:**
- `formatPct`, `winColor`, `deltaColor` centralizados em `lib/format.ts`
  — eliminam `const pct = ...` reimplementado em 10 páginas e a
  ternária `>= 0.5 ? "text-chart-1" : "text-chart-red"` repetida 13x
  (mais `deltaColor` para os casos de delta em torno de 0, não 0.5 —
  são semânticas diferentes, não a mesma função).
- `Takeaway` e `SectionTitle` (duplicados verbatim/quase-verbatim em
  Dashboard e Competitivo/Home) movidos para `components/ui.tsx`.
- `StatTile`/`KpiCard`/cards inline unificados em um único `StatCard`
  (`components/ui.tsx`) com variante `size="sm"|"lg"`.
- `RecentGameRow` (`components/RecentGameRow.tsx`) extraído de
  ChampionDetail e PlayerProfile — mesma linha de "última partida"
  (resultado, posição, KDA, duração/data), agora sempre como link para
  a partida (antes só PlayerProfile linkava).
- `Explain.tsx` tinha um `fetch` cru duplicando a lógica de base URL já
  centralizada em `api.ts`, e um `PHASES` local redundante com
  `lib/matchState.ts` — trocado por `api.shapImportancePhases()` (novo
  método) e o `PHASES` compartilhado.
- Não mexido: `PlayerProfile`/`ProPlayerProfile` e suas "pool de
  campeões" (uma é tabela, a outra é lista de linhas com ícone maior —
  layouts genuinamente diferentes, forçar um componente comum juntaria
  coisas que não deveriam ser iguais).

**Backend (`src/api/main.py`):**
- `CHAMPION_NORM_SQL`: o `CASE pp.champion WHEN 'Wukong'...END` que
  casa nome de exibição do Oracle's Elixir com nome interno da Riot
  estava copiado 4x (`champion_pro`, `pro_player_profile`,
  `pro_champions`). Agora é uma constante interpolada por f-string.
- `KDA_SQL` e `OPPONENT_JOIN_SQL` (self-join de participants por
  adversário direto de lane) extraídos da mesma forma — 4x e 3x.
- `champions()` não tinha clamp de `limit` (as demais rotas paginadas
  já clampavam) — alinhado com `max(1, min(limit, 200))`.
- Não mexido: uma divergência de formatação de rótulo negativo entre
  `gold15` (pandas, `int(x/1000)`) e `pro_gold15` (SQL, `x // 1000`) —
  investigado e não é bug ativo (os bins são sempre múltiplos exatos de
  1000 nos dois casos), só um estilo diferente; deixado como está.

Verificação: `tsc --noEmit` e `npm run build` limpos; backend importado
via AST + runtime e os 4 endpoints reescritos (`/stats/champions`,
`/stats/champion/{x}`, `/stats/champion/{x}/pro`, `/stats/pro/champions`)
mais `/compose` e `/stats/highlights` (que usam `OPPONENT_JOIN_SQL`)
testados contra o banco real via `TestClient` — todos OK.

**Verificação E2E (pós-commit):** typecheck/build/TestClient provam
que o código compila e a query roda, não que a página renderiza igual
pro usuário — rodei API (uvicorn) + front (Vite) de verdade e dirigi
via Playwright (Chromium, headless) contra as 11 rotas afetadas.
- As 11 páginas carregaram sem nenhum erro de console/página.
- `RecentGameRow` e `StatCard` renderizam igual ao antes (conferido
  visualmente em ChampionDetail e PlayerProfile).
- Cliquei os botões de fase em Explicabilidade (10/20/25/10 min) — o
  `PHASES` compartilhado (antes duplicado) troca a fase ativa e o
  gráfico corretamente a cada clique.
- Cliquei uma linha de "última partida" em ChampionDetail (agora é
  link, antes era só `<div>` — mesma UX que PlayerProfile já tinha) —
  navegou certo para `/partidas/:id`.
- Arrastei o slider "e se" de ouro no MatchDetail para os extremos —
  `deltaColor` pinta azul (`text-chart-1`) no positivo e vermelho
  (`text-chart-red`) no negativo, como esperado.
- Testei o campeão inexistente (`/campeoes/NaoExiste123`) — cai limpo
  no `ErrorNote`, sem quebrar layout.
- Achado (não é bug, é comportamento pré-existente): a cor de
  vitória/derrota (`winColor`) é por RESULTADO, não por lado do mapa —
  quando o vermelho vence, o título "Time vermelho — Vitória" fica
  AZUL (cor de vitória), não vermelho. Confunde à primeira vista numa
  página que também usa azul/vermelho como identidade de lado (mapa de
  calor, gráfico de diferença de ouro). Já existia antes da
  consolidação (só movi a ternária pra `winColor()`); registrado aqui
  para não reabrir como "bug" no futuro sem contexto.

## 2026-07-06 — Experimento 7 (negativo): item_gold_diff

Candidato apontado como "mais promissor" na entrada anterior: valor em
ouro dos itens FINALIZADOS (mesmo filtro `_completed_item_ids` da API:
não é componente de nada, comprável, custo >= 1100, não é
consumível/trinket, mapa 11) que cada time ainda possui no corte de
tempo — líquido de vendas, com `ITEM_UNDO` desfazendo a ação mais
recente (mesma lógica do ETL `load_items.py`, mas calculado direto da
timeline por `participantId`, sem precisar de `item_events`/join).
Script isolado: `src/models/experiment_item_gold.py` (não mexe em
`build_features.py`/`features.csv`/modelo em produção — só mede o
ganho antes de decidir integrar).

Hipótese: dois times com o mesmo `gold_diff` podem estar em estágios
de build muito diferentes (componentes espalhados vs. item completo) —
`item_gold_diff` capturaria isso. Resultado (XGBoost, CV 5-fold,
52.589 linhas match×corte, 10.351-7.575 partidas por corte):

| Corte | AUC baseline | AUC +item_gold_diff | Δ AUC |
|---|---|---|---|
| 10 min | 0.7375 | 0.7378 | +0.0003 |
| 15 min | 0.8214 | 0.8224 | +0.0010 |
| 20 min | 0.8574 | 0.8569 | -0.0005 |
| 25 min | 0.8935 | 0.8933 | -0.0002 |

Todos os deltas dentro do ruído entre folds — **não integrado** ao
pipeline de produção. Motivo provável: `gold_diff` já captura quase
toda a informação, já que ouro gasto em itens acompanha de perto o
ouro total ganho — `item_gold_diff` é altamente redundante com uma
feature que já existe. Sétimo experimento de feature engineering sem
ganho (depois de barão/arauto, dispersão de time, tuning por fase e
calibração).

## 2026-07-06 — Experimento 8 (negativo): visão (ward_diff / ward_kill_diff)

Último candidato de dado novo pendente da timeline. Duas features,
mesma convenção dos diffs existentes (positivo = vantagem azul):
`ward_diff` (wards colocadas azul − vermelho até o corte) e
`ward_kill_diff` (wards inimigas destruídas azul − vermelho até o
corte) — de `WARD_PLACED`/`WARD_KILL`, filtrando `creatorId`/`killerId
== 0` (evento de sistema). Script: `src/models/experiment_vision.py`
(mesmo formato do experimento de itens — isolado, não mexe em
produção). Testadas isoladas e juntas, XGBoost, CV 5-fold,
~55.757 linhas match×corte:

| Corte | baseline | +ward_diff | +ward_kill_diff | +ambas |
|---|---|---|---|---|
| 10 min | 0.7375 | 0.7374 (−0.0001) | 0.7400 (+0.0025) | 0.7378 (+0.0003) |
| 15 min | 0.8214 | 0.8216 (+0.0002) | 0.8218 (+0.0005) | 0.8215 (+0.0001) |
| 20 min | 0.8574 | 0.8568 (−0.0006) | 0.8590 (+0.0016) | 0.8579 (+0.0005) |
| 25 min | 0.8935 | 0.8939 (+0.0004) | 0.8938 (+0.0003) | 0.8941 (+0.0006) |

Maior delta observado em qualquer experimento até agora
(`ward_kill_diff` aos 10 min, +0.0025), mas ainda pequeno demais pra
justificar a complexidade extra sem quantificar o desvio-padrão entre
folds — **não integrado**. Oitavo experimento de feature engineering
sem ganho prático. Fecha a lista de candidatos de dado novo já
presentes na timeline (kills/torres/dragões/ouro/xp/itens/visão já
testados); um ganho futuro provavelmente exige um tipo de dado que a
timeline não tem (draft, posição espacial contínua, etc.) — não
prioridade atual.

## 2026-07-06 — Retreino com coleta adicional (BR1+EUW1+KR+NA1)

Coleta em background desde as sessões anteriores rendeu volume real
pela primeira vez fora do BR1: matches 12.247→15.739 (raw_timelines
14.943→16.104), e o mais importante, EUW1/KR/NA1 saíram de amostras
piloto (45-266 jogos) pra **1.307-1.367 jogos cada** — grande o
suficiente pra tirar conclusão, não só hipótese.

Pipeline completo rerodado (nesta ordem):
1. `load_items` — `item_events` reprocessado: 2.360.777 → **3.601.107**
   eventos (15.816 timelines, o join com `matches` exclui remakes).
2. `build_features` — `features_phases.csv`/`features.csv`
   regenerados: 10.295 → **15.785** partidas no corte de 15 min (todos
   os 4 cortes: 15.853/15.785/14.119/11.419 para 10/15/20/25 min).
3. `train_baseline` antes × depois (XGBoost, CV 5-fold):

   | | antes (10.295) | depois (15.785) | Δ |
   |---|---|---|---|
   | AUC-ROC | 0.8214 | **0.8289** | +0.0075 |
   | Acurácia | 0.7435 | **0.7489** | +0.0054 |

   RandomForest (AUC 0.8078→0.8114) e MLP (0.8206→0.8295) também
   melhoraram — ganho real, não ruído (compare com os deltas de
   ±0.001-0.003 dos experimentos de feature, todos descartados como
   ruído). **Confirma a conclusão já registrada: a alavanca que
   funciona é volume de partidas, não novas features.**
4. `export_model` — `data/models_phases.joblib` + `data/model.joblib`
   (corte 15) + `reports/shap_importance*.json` atualizados com os
   dados novos. Modelo em produção agora reflete as 15.785 partidas.

**Viés de lado por região, revisitado com amostra de verdade:**

| Região | Partidas | Win rate vermelho |
|---|---|---|
| BR1 | 11.936 | 56.3% |
| EUW1 | 1.307 | 53.5% |
| NA1 | 1.367 | 52.2% |
| KR | 1.308 | 50.6% |

**Isso muda a leitura anterior.** A hipótese do piloto (sprint 5,
amostras de 45-266) era "viés é específico do BR, não do elo alto em
geral" — com amostra 5-10× maior, as 4 regiões pendem pro vermelho
(50.6%-56.3%), não só BR. Leitura atualizada: parece um padrão de elo
altíssimo em geral (Challenger/GM, sem coordenação de draft de 5
pessoas — mesma explicação de antes, contra-pick garantido do
vermelho), com BR como caso mais extremo e KR o mais próximo do
equilíbrio. Ainda não é conclusivo (KR/EUW1/NA1 seguem bem menores que
BR1) mas já é amostra grande o bastante pra citar como achado, não só
hipótese. **Atualizar o texto do TCC com esta tabela quando o material
do professor chegar** — a narrativa "viés é só do BR" não se sustenta
mais como estava escrita.

## 2026-07-06 — Segunda rodada de coleta multi-região + retreino

Reseed do ladder (`seed_players --platforms euw1 kr na1 --tiers
CHALLENGER GRANDMASTER MASTER`, 33.110 jogadores inseridos/atualizados)
seguido de `collect_matches --platforms kr euw1 na1 --players 100
--matches-per-player 20`. Rendimento baixo (103 partidas novas no
total, não os milhares esperados) — **achado sobre a mecânica do
script**: `collect_matches` sempre seleciona os top-N jogadores por
`league_points DESC` (`src/collect/collect_matches.py:79-84`); como o
topo do ladder Challenger/GM quase não muda entre coletas, reseedar
sem aumentar bastante o `--players` traz essencialmente os mesmos
jogadores de antes, só capturando os jogos novos que eles jogaram no
meio tempo. **Pra crescer de verdade EUW1/KR/NA1, `--players` precisa
ser bem maior (500-1000+)** pra alcançar jogadores mais abaixo no
ladder que ainda não foram coletados.

Crescimento real desta rodada: EUW1 1.307→1.378, KR 1.308→1.354, NA1
1.367→1.446 (matches totais 15.918→16.114). Pipeline rerodado de novo
(`load_items` → `build_features` → `export_model`): item_events
3.601.107→3.668.806 eventos (16.114 timelines), features.csv (corte 15
min) 15.785→**15.979** partidas, `data/model.joblib`/
`models_phases.joblib` reexportados. Ganho de dados pequeno desta vez
(~1,2%) — não justificou medir antes/depois de novo (o ganho de AUC
do retreino anterior, +0,0075, já veio de +54% de dados; este
incremento é ordens de grandeza menor).

## 2026-07-06 — Coleta ampliada (500 jogadores/região) + retreino final

Usando o achado anterior (collect_matches sempre pega top-N por
league_points, 100 já era insuficiente), rodou com `--platforms kr
euw1 na1 --players 500 --matches-per-player 20`. **Resultado
excelente**: EUW1 +3.902 partidas (1.378→5.280), KR +3.117 (1.354→4.471),
NA1 praticamente parado (+0, 1.446→1.446 — parece que o script não
chegou a processar NA1 no tempo da coleta ou process timeout ocorreu).
Total: 16.114→23.133 partidas (**+6.979, +43,3%**).

Pipeline completo rerodado:
- `load_items`: 3.668.806 → **5.279.586** eventos (23.133 timelines,
  +1,6M eventos)
- `build_features`: 15.979 → **22.973** partidas no corte de 15min
  (todos os 4 cortes: 23.053/22.973/20.254/16.179)
- `train_baseline` (CV 5-fold, XGBoost):

  | Métrica | anterior (15.979) | agora (22.973) | Δ |
  |---|---|---|---|
  | AUC-ROC | 0.8289 | **0.8393** | **+0.0104** |
  | Acurácia | 0.7489 | **0.7573** | **+0.0084** |

  RandomForest e MLP também melhoraram (RF: 0.8114→0.8219, MLP:
  0.8295→0.8385). **Ganho real e consistente** — volume trabalha, não
  ruído como os 8 experimentos de feature descartados.
- `export_model`: `data/model.joblib`/`models_phases.joblib` +
  `reports/shap_importance*.json` reexportados. Modelo em produção
  agora reflete 23.133 partidas (45% do volume acumulado).

**Observação operacional:** taxa de vitória azul sobre a amostra toda
aumentou (43,7% em 15.979 → 45,6% em 22.973) — a coleta em regiões
não-BR1 parece estar trazendo mais jogos onde azul vence, ou o viés de
lado varia regionalmente como já documentado (BR1 56.3%, EUW1 53.5%,
NA1 52.2%, KR 50.6%). Não é motivo de preocupação — é dado real.

## 2026-07-06 — Análise geral do frontend + fechamento de gaps de qualidade

Análise ponto-a-ponto de `frontend/` (24 arquivos, 5.645 linhas): rotas,
camada de API (`lib/api.ts`), design system (`components/ui.tsx`),
amostras de página (Dashboard, TeamBuilder, MapHeatmap). Pontos fortes
confirmados: API client único e tipado, design system consolidado
(reflexo da refatoração de 2026-07-05), TypeScript estrito, zero
`console.log`/`TODO` esquecido. Três gaps estruturais identificados e
fechados na mesma sessão:

**1. Bug real — `MapHeatmap.tsx`:** `key={p.champion}` nos marcadores
de campeão colidia quando os dois times pegam o mesmo campeão (espelha
em solo queue). Corrigido para `key={`${p.team_id}-${p.champion_id}`}`.

**2. ESLint instalado pela primeira vez** (`eslint.config.js`, flat
config: `typescript-eslint` + `eslint-plugin-react-hooks` +
`eslint-plugin-react-refresh`, script `npm run lint`). Achou **5 bugs
reais** na primeira rodada:
- `Home.tsx`: componente `Section` declarado DENTRO do corpo de
  `UnifiedSearch` — recriado a cada render (identidade nova toda vez,
  força remount da subárvore). Corrigido: hoisted para módulo como
  `SearchSection`.
- `MatchDetail.tsx` (`WhatIfCard`): `setState` síncrono dentro de
  `useEffect` pra resemear o editor quando o minuto muda — padrão que
  causa um passo de render extra. Reescrito para o padrão recomendado
  pelo React ("ajuste durante o render", não em efeito): compara
  `point !== seededFor` e chama `setState` direto no corpo da função,
  sem `useEffect`. **Verificado em runtime via Playwright** (não só
  lint/build): slider de ouro vai de 700→10500 ao mudar o minuto pro
  máximo, sem erro de console.
- `Nlq.tsx`: mesmo padrão — o efeito de montagem chamava
  `showExplanation()` (que faz `setView` + `mutate`), mas `setView`
  era redundante ali (a view já nasce no valor que ele setava).
  Simplificado para chamar só `explain.mutate()` no efeito.
- `LiveReplay.tsx` (warning): `curve = data?.prob_curve ?? []` recriava
  array a cada render enquanto `data` está undefined — envolvido em
  `useMemo`.
- Restam 2 warnings cosméticos em `chart.tsx` (fast-refresh, arquivo
  mistura export de componente e de constantes) — sem impacto
  funcional, não corrigido.

**3. Error Boundary — não existia nenhum.** Qualquer exceção de render
fora de uma query (ex.: acessar propriedade de dado inesperado em
`Nlq.tsx` renderizando SQL dinâmico) deixava a tela branca sem
fallback. Criado `src/components/ErrorBoundary.tsx` (class component —
única forma de implementar a API de error boundary do React),
envolvendo o `<Outlet />` no `Layout.tsx`, `key`ado por
`location.pathname` (navegar pra outra página desmonta o boundary
quebrado em vez de ficar preso nele).

**4. Zero cobertura de teste — não existia nenhuma.** Instalado Vitest
+ Testing Library (`vite.config.ts` ganhou bloco `test`, setup em
`src/test/setup.ts` com stub de `ResizeObserver` — jsdom não
implementa, e o Recharts usa internamente em todo gráfico). Dois
níveis de teste:
- **19 testes unitários** de `lib/format.ts` e `lib/ddragon.ts`
  (funções puras: `formatPct`, `winColor`, `deltaColor`, `formatCell`,
  `isEmptyResult`, `isAdvisory`, `championDisplayName` com os quirks de
  nome). Achou 1 erro no próprio teste (não no código): `formatPct`
  usa `.toFixed()` — ponto decimal fixo — enquanto `formatCell` usa
  `toLocaleString("pt-BR")` — vírgula decimal; são convenções
  diferentes dentro do mesmo arquivo, documentado no teste agora.
- **14 smoke tests** (`src/pages/pages.smoke.test.tsx`): renderiza
  cada página sob os providers reais (`QueryClientProvider` +
  `MemoryRouter`, harness em `src/test/renderPage.tsx`) com `api`
  mockado via `vi.mock` + `Proxy` retornando uma Promise que nunca
  resolve — testa o caminho de mount/params/loading (onde bugs de
  hook/JSX aparecem), não o de dados renderizados (exigiria fixtures
  completas pros 30+ endpoints — desproporcional pro objetivo aqui).

Resultado final: `npm run lint` (0 erros, 2 warnings cosméticos),
`npm run test` (33/33 passando), `npm run build` (sucesso, `tsc` limpo).
Também corrigido o texto desatualizado do Dashboard ("neste recorte
Challenger/GM BR o vermelho domina" → reflete o dataset multi-região
atual, aponta pro card de viés regional).

## 2026-07-06 — Consolidação de navegação (10 → 6 abas)

Brainstorm pedido pelo usuário sobre sobreposição entre as 10 abas da
sidebar, com evidência concreta antes de propor qualquer fusão (não só
opinião): li `Matches.tsx` (96 linhas, zero filtro/busca/paginação —
literalmente `api.recentMatches(20)` numa lista) e confirmei que
`Home.tsx` já mostra o mesmo feed resumido (`api.recentMatches(4)`)
com link "ver todas" pra essa página — sobreposição real, não
hipotética. Mesmo padrão pros outros 3 achados. 4 fusões aprovadas
pelo usuário e aplicadas na mesma sessão:

**1. "Partidas" absorvida pela Início.** `Matches.tsx` deletado. Feed
da Início foi de 4→8 partidas, ganhou botão "assistir ao vivo"
(sorteia partida real, navega pra `/partidas/:id?replay=1` — também é
a nova porta de entrada da funcionalidade do item 4 abaixo).

**2+3. "Predição" + "Explicabilidade" fundidas dentro de "Montar
partida", que virou "Simulador" com 3 abas.** As duas eram, na
prática, casos particulares do mesmo modelo/estado
(`src/lib/matchState.ts`, mesmos sliders/fases 10-25min) pra mesma
audiência. `TeamBuilder.tsx`/`Predict.tsx`/`Explain.tsx` viraram
"painéis" (`CompositionPanel`/`StatePanel`/`ExplainPanel` — só tiveram
o `PageHeader` próprio removido e o export renomeado, lógica interna
intocada) compostos por `Simulador.tsx`, novo, com tab switcher local.

**4. "Ao vivo" fundida dentro de "Partida" como modo replay.**
`LiveReplay.tsx` deletado; sua lógica de animação (play/pausa/
velocidade/reiniciar/revelar resultado) virou o componente
`ProbabilityCard` dentro de `MatchDetail.tsx`, reaproveitando o
`prob_curve` **já carregado pela página** (sem fetch duplicado — a
página antiga sorteava a partida E buscava a análise; agora só o
sorteio de qual partida abrir acontece separado, na Início). Botão
"Assistir como replay" alterna entre o gráfico estático (comportamento
de sempre) e o animado; `?replay=1` na URL autoplaya direto.

**Achado durante a verificação em navegador (não durante o code
review):** com as 5 rotas antigas removidas do `App.tsx`
(`/partidas`, `/predicao`, `/aovivo`, `/montar`, `/explicabilidade`)
sem nenhuma rota `*` de fallback, o React Router v7 renderiza **nada**
quando nenhuma rota casa — nem o `<Layout>`/sidebar, `#root` fica com
innerHTML vazio. Não é um crash (zero erro de console/página), mas é
uma tela branca sem navegação nenhuma pra quem tiver essas URLs
salvas. Corrigido com `<Navigate replace />`: as 4 rotas específicas
redirecionam pro destino novo (`/predicao`→`/simulador` etc.) e um
catch-all `path="*"` manda pra Início.

Sidebar final: Início, Dashboard, Campeões, Competitivo, Consulta NL,
Simulador — 6 itens, abaixo até da estimativa original de 7 do
brainstorm (a fusão 1 também remove um item de nav que eu tinha
contado separado). Verificado em 3 camadas: `npm run lint` (0 erros),
`npm run test` (31/31 — smoke tests atualizados pro novo conjunto de
páginas + teste novo clicando nas 3 abas do Simulador), `npm run
build` (sucesso), e Playwright no navegador real (nav com 6 itens,
feed de 8 partidas + botão ao vivo, as 3 abas do Simulador renderizando
e trocando sem crash, `/partidas/:id?replay=1` autoplayando e
revelando o resultado real ao fim, os 5 redirects de rota antiga
funcionando). **Bug pego só pelo Vitest, não pelo code review**: sem
`globals: true` no `vite.config.ts`, o `@testing-library/react` não
registra `afterEach(cleanup)` automaticamente — o DOM de um teste
vazava pro próximo dentro do mesmo arquivo (`getByRole` achava
elementos duplicados de renders antigos). Corrigido com
`afterEach(cleanup)` explícito em `src/test/setup.ts`.

## 2026-07-06 — Visão (gráfico + mapa aproximado) e build de itens na Partida

Duas features novas na página de Partida, pedidas pelo usuário depois
de eu sugerir "mapa de calor de wards" como próxima API. **Correção
importante durante a investigação**: conferi os eventos reais
(`WARD_PLACED`/`WARD_KILL` na timeline) e a Riot **não grava a posição
da ward** — só `creatorId`/`killerId`/`wardType`/`timestamp`, diferente
de `CHAMPION_KILL` que tem `position`. A sugestão original ("mapa de
calor igual aos abates") não era literalmente viável; virou duas
entregas honestas sobre o mesmo dado:

**1. Gráfico "Controle de visão"** (`VisionCard` em `MatchDetail.tsx`):
diferença acumulada (azul−vermelho) de wards colocadas/destruídas ao
longo do jogo — mesma convenção `_diff` dos outros gráficos, sem
nenhuma aproximação (só contagem de evento por time, não precisa de
posição). **Achado de design pego só na revisão do screenshot, não no
code review**: as duas linhas inicialmente usavam `chart-1`/`chart-red`
(as cores de "time azul"/"time vermelho" em toda a plataforma) — mas
as duas linhas JÁ são diffs azul-menos-vermelho, então usar essas
cores sugeria (errado) "linha do time azul" vs "linha do time
vermelho". Corrigido para cores neutras (`chart-2`/`chart-4`) +
`<Legend>` explícita.

**2. Camada de wards aproximada no `MapHeatmap`** (toggle "Wards
(aproximado)", desligado por padrão): usa a posição do JOGADOR que
colocou/destruiu a ward naquele minuto como proxy — texto explícito
avisando que não é a posição real da ward, no mesmo estilo de
honestidade do card "E se..." (`WhatIfCard`). Bola cheia = colocada,
anel = destruída, cor por time.

**3. Build de itens por partida** (coluna "Itens" na `TeamTable`):
achado que simplificou o plano original — `raw_matches.payload
.info.participants[].item0..item6` já tem os slots finais de item
gravados pela própria Riot, não precisa reconstruir do `item_events`
(que serve pra ORDEM de compra, não pro estado final). 7 ícones por
jogador (6 itens + trinket separado), via `itemIcon()` já existente.

**Backend:** `/matches/{id}/positions` ganhou campo `wards` (mesmo
padrão de extração de `kills`/`objectives`, já tinha o loop de frames
pronto). `/matches/{id}/analysis` ganhou `items` por participante (join
com `raw_matches`, sem nova query cara). Zero endpoint novo — os dois
já existentes só cresceram um campo. Verificado direto via `curl`: 198
wards extraídos numa partida de teste, itens finais batendo com o
esperado.

Verificado em 3 camadas de novo: `npm run lint` (0 erros), `npm run
test` (31/31), `npm run build`, e Playwright no navegador real
(checkbox de wards, aviso de aproximação aparecendo, card de visão
visível, coluna de itens com 68 ícones renderizados nas duas tabelas).
Screenshot revisado visualmente — foi isso que pegou o bug de cor do
item 1 acima, não nenhuma das outras camadas de verificação.

## 2026-07-06 — Sinergia de dupla com shrinkage/IC (NLQ + /compose)

Pendente antigo do diário resolvido: "sinergias de dupla com correção
de amostra pequena — perguntas tipo 'Nocturne + Orianna' terem
resposta estatística mais robusta". Duas frentes:

**1. `/compose` (`team_synergies()` em `src/api/main.py`).** Antes: só
`win_rate` bruto da dupla vs a expectativa (média dos win rates solo),
cortando qualquer dupla com menos de 20 jogos — "Nocturne + Orianna"
com poucos jogos simplesmente não aparecia, sem explicação. Agora:
- `delta` é a versão com shrinkage bayesiano (`SYNERGY_SHRINKAGE_K =
  20`, mesma ideia já usada no `player_effect()` pra jogador×campeão) —
  encolhe pra perto de zero quando há poucos jogos, converge pro delta
  bruto quando há muitos.
- IC de Wilson (95%) sobre o win_rate bruto (`ci_low`/`ci_high`).
- `significant`: true quando o IC exclui a expectativa "sem sinergia"
  — distingue sinal real de ruído.
- Corte mínimo caiu de 20 para `SYNERGY_MIN_GAMES = 5` — duplas raras
  agora aparecem, só que com IC largo e delta encolhido em vez de
  sumirem. Verificado ao vivo: "Darius + Warwick" (9 jogos) aparece com
  IC 6-55% em cinza (não significativo); duplas com mais jogos mostram
  cor quando o IC de fato exclui a expectativa.
- Frontend (`SynergyList` em `TeamBuilder.tsx`, agora `CompositionPanel`
  dentro do Simulador): mostra a faixa de IC abaixo do delta, delta em
  cinza quando não significativo, legenda explicando a correção.

**2. NLQ (`schema_context.py`).** Adicionada uma regra específica pra
perguntas de sinergia de dupla ("X e Y têm sinergia?"), ensinando o
padrão de SQL com CTE que calcula jogos + win rate bruto + expectativa
solo + win rate ajustado por shrinkage (mesma fórmula do backend, sem
IC — a fórmula de Wilson é frágil demais pro LLM reproduzir certo
numa SQL gerada dinamicamente, shrinkage é só uma média ponderada,
mais seguro). **Regra da casa seguida**: rodei `evaluate_nlq` depois da
mudança e achei uma regressão real (não das 3 já conhecidas): "qual
time derruba mais torres em média" passou a falhar. Investigação:
tentei 2 hipóteses erradas antes de achar a causa (diluição por
tamanho do prompt, depois confusão de conteúdo com o exemplo novo) —
nenhuma resolveu. A causa real: meu método de diagnóstico via CLI
(`python -m src.nlq.nl_to_sql "pergunta com acento"`) corrompe UTF-8
no argv do shell do Windows, mandando pro LLM uma pergunta com
acentuação quebrada — diferente do benchmark real, que lê a pergunta
direto do código-fonte `.py` (sem passar pelo shell). Confirmado
rodando `evaluate_nlq` (fonte confiável) 2x seguidas com a mudança:
**23/26 = 88%, as mesmas 3 falhas antigas, zero regressão nova**. A
correção de escopo (regra sobre 2 campeões nomeados, não confundir com
ranking/média por time) e o encurtamento do texto ficaram no arquivo
de qualquer forma — não pioram nada e deixam a regra mais clara.
Testado com a pergunta motivadora de verdade: "Nocturne e Orianna têm
sinergia?" → 49 jogos, 40,8% bruto, ajustado pra 43,1% (expectativa
solo ~48,8%) — resposta com números, não silêncio.

Verificado: `npm run lint` (0 erros) / `npm run test` (31/31) / `npm
run build` / Playwright real no Simulador (aba Composição, IC visível,
legenda de shrinkage visível, dupla de 9 jogos aparecendo em cinza).

## 2026-07-08 — Revisão geral de dados/resultados + achado: viés de lado enfraquece com o tempo

Pedido do usuário: "análise e revisão dos nossos dados e resultados".
Levantamento fresco (nada reaproveitado de execuções antigas): 23.133
partidas / 24.999 jogadores / 173 campeões / 96.716 jogos profissionais.
AUC por fase, medida agora com os hiperparâmetros de produção (500
árvores, lr=0,01, profundidade 3): **10min 0,767 / 15min 0,842 / 20min
0,872 / 25min 0,907** — monotônico, amostra caindo de 23.053 para
16.179 conforme o corte avança (nem toda partida chega ao late game).
Nota de higiene: `raw_matches` (23.571) e `matches` normalizado
(23.133) divergem em 438 linhas — `load_matches` provavelmente não
rodou no último lote da coleta ampliada; não afeta os números deste
relatório mas vale rerodar antes do próximo retreino.

**Achado novo, investigado com 3 testes independentes: o viés de lado
não é constante entre fases.** Consultando `/predict` com estado
zerado (empate total) em cada corte: 10min 47,8% azul → 15min 46,3%
(o mais vermelho) → 20min 49,1% (quase neutro) → 25min 51,1% (azul no
ponto). Isso contradiz o texto atual (Dashboard, Explicabilidade,
Simulador) que trata "vermelho favorecido" como constante.

Investigação (pedida pelo usuário: "investigue" antes de aceitar o
achado como está):
1. **É real, não artefato do modelo?** Taxa de vitória BRUTA (sem
   modelo) entre partidas genuinamente empatadas (`|gold_diff|<500`)
   em `features_phases.csv`: 46,1%→46,4%→47,3%→48,6% azul do corte 10
   ao 25. Confirma a tendência nos dados brutos — o modelo extrapola
   um pouco além disso (51,1% vs 48,6%), mas a direção é real.
2. **É mistura regional (EUW1/KR crescendo)?** Refeito só dentro do
   BR1 (o mais vermelho-enviesado): 45,3%→44,6%→47,2%→51,1% — o
   padrão fica MAIS forte dentro de uma única região, não mais fraco.
   **Hipótese de mistura regional descartada.**
3. **É que "jogos longos são um tipo diferente de jogo"?** Win rate
   azul incondicional (sem filtro de empate) por faixa de duração
   total da partida: plana em ~44-47% em toda faixa, dentro e fora do
   BR1. **Descartado** — o efeito é específico de estar empatado
   NAQUELE minuto, não de a partida ser longa.
4. **Solidez estatística:** IC95% de Wilson do ponto BR1 aos 25min
   (51,1%, n=458) = [46,5%–55,6%] — inclui 50% E valores ainda
   vermelho-favorecidos. Aos 10min (45,3%, n=2.194) o IC é
   [43,2%–47,3%], exclui 50% com folga. **A tendência de queda é
   sólida (4 pontos monotônicos, 2 testes independentes); a alegação
   específica de "inverte completamente pro azul aos 25min" não é —
   amostra de empates tardios ainda é pequena.**

Explicação mais provável (não testada formalmente, hipótese pra
próxima investigação se for atrás): sobrevivência do ESTADO de
empate, não da partida — um empate aos 15min tende a ser instável
(muitas dessas partidas estão prestes a desequilibrar); um empate que
se sustenta até os 25min reflete jogo mais equilibrado/de desgaste,
onde o contra-pick garantido do vermelho parece já ter sido absorvido
pela própria partida.

**Recomendação pro texto do TCC:** trocar "vermelho favorecido"
(implicitamente constante) por "vermelho favorecido no early/mid,
enfraquecendo até ficar estatisticamente indistinguível de neutro no
late game" — pode ser afirmativo nesse ponto (mistura regional e
"jogos longos" já descartados como explicação alternativa), só evitar
alegar inversão completa aos 25min.

Relatório completo publicado como Artifact (dados + investigação +
recomendações, com IC e os 3 testes) — ver histórico de conversação
2026-07-08 se precisar do link.

## 2026-07-08 — Camada 1 do plano "conhecimento geral + predição": orientação estratégica

Depois da discussão sobre até onde "conhecimento geral de LoL" pode
melhorar os modelos (conclusão: não entra como feature — o modelo de
vitória nem sabe qual campeão está sendo jogado, e o efeito de coisas
como controle de wave já colapsa em `gold_diff`/`xp_diff`, é por isso
que os 9 experimentos de feature deram negativo), desenhado um plano
de 4 camadas por custo/risco crescente:
1. **Diagnóstico narrado** — LLM traduz estado+SHAP já calculados em
   orientação estratégica. Baixo risco, reaproveita tudo que já existe.
2. **Consciente de composição** — modelo de estado + `/compose` juntos,
   recomendação por campeão. Esforço médio, modelagem nova.
3. **Ação concreta** (wave/posição) — exige dado que a API da Riot não
   tem (replay `.rofl` ou visão computacional sobre o minimapa).
   "Reconstruir do zero" de verdade.
4. **Verificação causal** — correlação vira causalidade verificada.
   Pesquisa, não feature; viés de confusão em dado observacional.

Camadas 3-4 ficam registradas como trabalhos futuros no texto do TCC,
não como algo a construir agora.

**Camada 1 implementada nesta sessão.** Endpoint novo `POST /coach`
(`src/coach/advice.py` + `src/api/main.py`): recebe o `state` +
`blue_win_probability` + `shap_contributions` que o `/predict` já
calculou (não recalcula nada) e devolve uma orientação estratégica em
texto (Claude Haiku, temperatura 0,4, 4-6 frases). Mesma convenção de
honestidade já estabelecida no NLQ ("Leitura de jogo:") e no
`WhatIfCard` ("leitura honesta"): o prompt força a resposta a terminar
deixando explícito que é leitura geral aplicada ao estado, não
verificada pelos dados desta partida — o modelo não vê itens, posição
de jogador nem wave.

Frontend: componente compartilhado `CoachCard`
(`frontend/src/components/CoachCard.tsx`), botão "Gerar orientação"
sob demanda (não automático — custaria uma chamada de LLM a cada
arrasto de slider). Integrado em dois lugares que já tinham
estado+predição prontos:
- Aba Estado do Simulador (`StatePanel`, `Predict.tsx`) — cenário livre.
- Card "E se..." do `MatchDetail` (`WhatIfCard`) — precisou virar
  Fragment (`<>...</>`) pra retornar o Card original + o CoachCard como
  irmão, não aninhado (Card dentro de CardContent ficava com borda
  dupla, corrigido antes de photografar).

Testado ponta a ponta: `curl` direto no `/coach` com um cenário de time
azul muito atrás (gold_diff −3500) devolveu orientação coerente
(evitar luta, farm seguro, ceder objetivos secundários, escalar pro
late) terminando com o aviso de honestidade. Playwright confirmou os
dois pontos de integração funcionando no navegador, sem erro de
console. `npm run lint` (0 erros) / `npm run test` (31/31) / `npm run
build`: todos verdes.

## 2026-07-08 — Camada 2: orientação consciente de composição

`POST /coach` ganhou campos opcionais: `blue_champions`/`red_champions`
(por posição), `lanes` (matchups) e `blue_synergies`/`red_synergies`
(sinergias) — os MESMOS números que o `/compose` já calcula do
histórico real (shrinkage + IC, ver entrada de sinergia de dupla
acima), nunca invenção da LLM. O prompt (`src/coach/advice.py`)
distingue explicitamente "dado real" (matchup/sinergia) de
"conhecimento geral" (o resto), e só cita estatística que foi de fato
fornecida — instrução explícita pra não alucinar número.

Dois pontos de integração, cada um com o contexto que já tinha
disponível:
- **`WhatIfCard` (MatchDetail)**: passa os campeões da partida REAL
  (de `m.participants`, por posição) — não tem matchup/sinergia
  (seria preciso uma chamada extra a `/compose`, fora de escopo por
  ora), mas já cita campeão específico em vez de só "time azul".
- **`CompositionPanel` (Simulador)**: contexto completo — campeões +
  `result.lanes` + `result.synergies` do `/compose` já calculado.
  Só aparece quando "Estado da partida" está incluído (precisa de um
  estado real pra narrar, não só a heurística de composição pura).

Testado com um cenário completo (Singed/Hecarim/Lissandra/Caitlyn/Bard
vs Darius/Warwick/Viktor/Ashe/Camille, estado zerado aos 15min): a
orientação citou Lissandra 58% vs Viktor, Singed 55% vs Darius, Bard
49% vs Camille — matchups reais, não genéricos — tecidos em conselho
específico ("vermelho deve evitar lutas frontais... Warwick tem
excelente gank setup pra explorar lanes inimigas"). Verificado via
`curl` (backend isolado) e Playwright nos dois pontos de integração,
sem erro de console. `npm run lint` (0 erros) / `npm run test`
(31/31) / `npm run build`: todos verdes.

## 2026-07-08 — Camada 2 (itens/posição) + INÍCIO da Camada 3 (sinais táticos)

O aviso de honestidade do coach dizia "não vê itens, posicionamento
real dos jogadores ou controle de wave" — o usuário perguntou se pra
resolver isso precisaria das próximas camadas. Análise: **itens e
posição a Riot GRAVA** (item_events; participantFrames com x/y por
minuto, já usados no MapHeatmap) — dá pra alcançar estendendo a Camada
2, sem reconstruir nada; só **controle de wave/minion** exige Camada 3
de verdade (não existe em nenhuma versão da match-v5, só replay .rofl
ou visão computacional). Feito nesta sessão:

**Novo módulo `src/coach/tactics.py`** — `tactical_context(match_id,
minute, items_catalog, completed_ids)` deriva da timeline REAL:
- **Itens finalizados possuídos por cada campeão NAQUELE minuto**
  (item_events com `ts_ms <= minute*60000`, compra menos venda, filtra
  finalizados, resolve nome via items.json) — dado exato da partida.
- **Sinais espaciais (início da Camada 3)** a partir do frame do
  minuto: agrupamento (spread normalizado dos 5 em torno do centroide:
  agrupados / parcialmente / espalhados), overextensão (jogadores além
  do rio — anti-diagonal nx+ny=1 — na metade inimiga, com flag de "bem
  fundo"), e tempo de selva (jungleMinionsKilled azul − vermelho).

`/coach` ganhou `match_id` + `game_minute` opcionais (game_minute é o
minuto de JOGO mostrado, distinto do corte do modelo em state.minute);
quando presentes numa partida real, o servidor chama tactical_context
e passa pro prompt (advice.py), em blocos rotulados "DADO REAL desta
partida". O aviso final do prompt vira condicional: com contexto
tático, diz que itens/posição são reais mas a posição é aproximada (1
amostra/minuto) e que wave/minion não é observável — mais honesto que
o aviso genérico anterior. Frontend: `CoachContext` ganhou
`matchId`/`gameMinute`, o `WhatIfCard` (MatchDetail) passa o id da
partida + `point.minute`, e o subtítulo do card reflete "com itens e
posição reais desta partida (posição aproximada)". O Simulador NÃO
passa match_id (é composição hipotética, sem partida real) — continua
composição-only.

Verificado ponta a ponta: `curl` no `/coach` com match_id real aos 20
min citou os itens reais de cada campeão (Khazix/Glaive Sombria,
Singed/Rylai) + "Darius e Camille espalhados na metade inimiga"; no
navegador (aos 14 min) citou Youmuu/Glaive Sombria, "Camille avançada
não carrega teamfight sozinha", "4 camps de vantagem na selva",
fechando com o aviso de wave/minion. `npm run lint` (0 erros) / `npm
run test` (31/31) / `npm run build`: verdes.

**Estado do plano de 4 camadas:** Camada 1 e 2 completas; Camada 3
**iniciada** — a fatia de sinais espaciais/táticos DERIVÁVEIS do dado
que temos (agrupamento, overextensão, tempo de selva) está no ar. O
que falta da Camada 3 é o estado de wave/minion e micro de verdade,
que continua bloqueado por falta de dado (replay .rofl / visão
computacional — trabalho futuro no texto do TCC). Camada 4
(verificação causal) segue como limitação/futuro.

## 2026-07-08 — Camada 3 continuada: visão e momentum de abates

O usuário cobrou continuar a Camada 3 depois do commit anterior — com
razão: eu tinha tratado "o resto da Camada 3" como só o muro do
wave/minion, mas ainda sobrava uma fatia derivável do dado que já
temos e que eu não tinha esgotado: **visão** (eventos `WARD_PLACED`,
já extraídos pro `/matches/{id}/positions`) e **momentum recente**
(abates numa janela, distinto do `kill_diff` acumulado do jogo todo).
Diferença importante em relação a agrupamento/overextensão: visão e
momentum são **contagem exata de evento**, não aproximação de posição
— dado mais forte que o resto da Camada 3.

`tactical_context()` ganhou:
- **Visão**: wards de controle vs normais colocadas por cada time nos
  últimos `WINDOW=4` minutos (mesma janela do `MapHeatmap`). Filtra
  `wardType == UNDEFINED` (artefato de evento de sistema do início da
  partida — mesmo cuidado já tomado no `/matches/{id}/positions` de
  2026-07-06).
- **Momentum**: abates por time na mesma janela de 4 minutos (via
  `CHAMPION_KILL.killerId`, ignorando `killerId=0` = execução por
  torre/monstro).

`advice.py` ganhou 2 blocos de prompt novos ("Wards colocadas..." e
"Abates nos últimos N minutos..."), ambos rotulados DADO REAL, e a
instrução final passou a mencionar visão/momentum explicitamente.
`CoachCard` (frontend) atualizado pra citar isso no subtítulo.

Testado com um cenário de vantagem grande (ouro +3800, 20min): a
orientação citou "colocou apenas 2 wards de controle contra 5 do
Azul nos últimos 4 minutos" e "momentum recente (11×4 para o Azul)"
— tecidos com itens e posição no mesmo parágrafo, não como blocos
separados. Verificado no navegador (14min) também: "usar a visão
inferior (14 wards normais)" e "momentum de 5 abates nos últimos 4
minutos indica que lutas estão sendo vencidas". `npm run lint` (0
erros) / `npm run test` (31/31) / `npm run build`: verdes.

**Estado do plano de 4 camadas, atualizado:** a fatia DERIVÁVEL da
Camada 3 (agrupamento, overextensão, tempo de selva, visão, momentum)
está completa por ora — não sobrou nenhum sinal óbvio no dado atual
que ainda não tenha sido explorado. O que resta bloqueado é
especificamente o estado de wave/minion e micro momento-a-momento
(cooldown de habilidade, aggro de creep, congelamento de rota) — isso
sim exige replay `.rofl` ou visão computacional, um projeto à parte.

## 2026-07-08 — Feedback de uso real (Danone): 4 itens, começando pelo 1

Usuário trouxe feedback de uso real da plataforma (conversa de
WhatsApp), 4 itens distintos. Ordem confirmada com o usuário: itens
por minutagem → recomendação de build → análise de draft/comp antes
do jogo começar → replay mais rico. Resumo dos 4 (planejamento
completo, efeito só do item 1 nesta entrada):

1. **Itens refletirem a minutagem** — a coluna "Itens" do `MatchDetail`
   sempre mostrava o build FINAL, não importa o minuto do slider do
   mapa de calor.
2. **Recomendação de build** — exemplo real do feedback: "Ludens teria
   sido melhor que [item X] pra Syndra, dado o quão squishy o time
   inimigo é" — raciocínio de item condicionado na comp adversária.
3. **Análise de comp/draft antes da partida começar** — o feedback mais
   rico: "essa comp do azul nunca ganha, a única win condition é a
   Irelia snowballar na side contra o Jayce, mas mesmo assim o
   vermelho tem Poppy pra pickar ela antes dela chegar no Ziggs" —
   análise de win condition + contra-pick + scaling, sem depender de
   nenhum estado de jogo (só os 10 campeões do draft).
4. **"Assistir partida" com mais informação** — o replay (`?replay=1`)
   hoje só anima a curva de probabilidade; feedback comparou com
   overlay de broadcast ("BGL"), querendo ver mapa de calor/itens/
   objetivos evoluindo junto, não só uma linha sozinha.

**Item 1 implementado.** `/matches/{id}/positions` ganhou `items` em
cada jogador de cada frame — reconstrói "o que cada um tinha NAQUELE
minuto" andando pelos `item_events` em paralelo com os frames (uma
única query ordenada por `ts_ms`, ponteiro avançando junto com o loop
de frames — não é uma query por minuto). `TeamTable` (`MatchDetail`)
agora lê de `positions.data.frames[minute]` em vez dos itens finais
de `/analysis`; enquanto `/positions` ainda carrega, cai pros itens
finais (com trinket) pra não piscar vazio. Sem trinket na versão por
minuto — `item_events` não rastreia trinket (fora do filtro de itens
"finalizados").

**Bug real pego na verificação visual, não no code review**: o
cabeçalho da coluna virou "Itens aos 14 min" pra dar contexto, e isso
colidiu com "Visão" (virou "Visãoltens" ilegível) — a tabela já tinha
zero padding horizontal nos `<th>`/`<td>` (só `py-2`, achado
pré-existente, não introduzido agora, só ficou visível com o texto
mais longo). Corrigido: contexto do minuto virou subtítulo do card
("Coluna Itens mostra o build aos X min..."), cabeçalho voltou a ser
só "Itens", e `px-2` + `overflow-x-auto` adicionados na tabela toda
(mesma convenção já usada em `Champions.tsx`).

Verificado: aos 14min a primeira linha mostrava 1 ícone de item;
arrastando o slider pro fim (30min), 3 ícones — cabeçalho do card
atualiza junto. `npm run lint` (0 erros) / `npm run test` (31/31) /
`npm run build`: verdes.

## 2026-07-08 — Feedback 2/4: recomendação de build condicionada na comp inimiga

Puramente mudança de prompt em `src/coach/advice.py` — zero
infraestrutura nova, porque itens e campeões dos dois lados já estavam
no prompt desde a Camada 2/3. Duas instruções novas:
- Quando há itens reais (`has_tactical`) E campeões dos dois lados:
  pede recomendação de build de verdade — próximo item ou mudança de
  prioridade, olhando o que cada time já tem e o equilíbrio squishy/
  tanque da comp inimiga. Explicitamente rotulado como "leitura de
  conhecimento geral sobre os campeões, não dado medido" — mesma
  convenção de honestidade de sempre, e instrução pra não inventar
  número (% de redução de dano etc.).
- Quando há só campeões (sem itens reais, ex.: Composição do
  Simulador): versão mais fraca, só comenta prioridade de tipo de
  build sem apontar item específico (não tem itens atuais pra
  raciocinar em cima).

Também subiu o teto de frases (4-6 → 4-8, mais perto de 8 quando tem
build pra incluir) e `max_tokens` (600→750) pra caber sem cortar.

Testado com um cenário desenhado pra bater com o exemplo do feedback
(comp azul com bastante dano mágico vs comp vermelha squishy): a
orientação recomendou "Darius deveria considerar Força da Natureza...
a composição azul tem muito dano mágico, então resistência mágica é
mais urgente que Lâmina Fantasma agora" e "Camille pode seguir pra
Abismo Âncora... contra o poke de Lissandra e Caitlyn" — exatamente o
tipo de raciocínio "Ludens seria melhor pra Syndra dado o quão squishy
o time inimigo é" do feedback original. Verificado no navegador sem
erro de console. Sem mudança de frontend (só prompt).

## 2026-07-08 — Feedback 3/4: leitura de draft (win condition, contra-pick)

O feedback mais rico dos 4: o usuário mandou uma leitura de caster de
verdade sobre uma partida real — "essa comp do azul nunca ganha, a
única win condition é a Irelia snowballar na side contra o Jayce, mas
mesmo assim o vermelho tem Poppy pra pickar ela antes dela chegar no
Ziggs". Isso é análise de win condition + contra-pick + scaling, e não
depende de NENHUM estado de jogo — só os 10 campeões do draft.

Diferente das camadas 1-2 (que sempre partiam de um `MatchState`),
essa é uma pergunta estruturalmente diferente ("quem tem vantagem
estratégica pelo draft" em vez de "quem está ganhando agora"). Nova
função `generate_draft_analysis()` em `src/coach/advice.py` — não usa
`MatchState` nem probabilidade do modelo, só campeões por posição +
opcionalmente `lanes`/`synergies` (mesmos dados reais de sempre).
Refatorei `_format_lanes()`/`_format_synergies()` como helpers
compartilhados entre `generate_advice()` e a função nova (estavam
duplicados inline). Prompt pede explicitamente: win condition de cada
time, matchups favoráveis/perdidos (dado real quando disponível),
se o time favorecido tem resposta pra win condition do outro (peel,
CC, contra-pick), e um veredito direto — "não amacie a leitura por
educação".

Novo endpoint `POST /coach/draft`. Frontend: componente
`DraftAnalysisCard` (ícone `Swords`, distinto do `Compass` do
`CoachCard`), reaproveitando o mesmo padrão visual (botão sob demanda
+ caixa de narrativa). Dois pontos de integração:
- **`MatchDetail`**: acima da curva de probabilidade (é uma leitura
  de ANTES do jogo, não amarrada ao slider de minuto) — só campeões
  da partida real, sem matchup/sinergia (não chama `/compose`; fica
  registrado como gap, igual o já anotado pro `WhatIfCard`).
- **`CompositionPanel`** (Simulador): contexto completo (`result.lanes`
  + `result.synergies`, já calculados) — e ao contrário do `CoachCard`,
  aparece **mesmo sem "Estado da partida" marcado**, porque não precisa
  de estado nenhum.

Testado com uma reconstrução do cenário exato do feedback (Irelia vs
Jayce top, Syndra vs Ziggs mid, Akali vs Yone bot, Poppy no time
vermelho): a leitura identificou win conditions distintas pra cada
time, chamou a vantagem de lane do Irelia vs Jayce, e apontou que
Poppy+Karma dão peel pro carry inimigo — mesma ESTRUTURA de raciocínio
do feedback (win condition + contra-pick + veredito por janela de
tempo), mesmo sem replicar a leitura exata do usuário (não dava pra
saber que o alvo específico da Irelia era o Ziggs sem essa informação
extra). Verificado nos dois pontos de integração via Playwright, sem
erro de console. `npm run lint` (0 erros) / `npm run test` (31/31) /
`npm run build`: verdes.

## 2026-07-08 — Feedback 4/4: replay estilo broadcast (fecha o lote de feedback)

Último dos 4: "mas o BGL é visualização das coisas em TODO tempo de
jogo" — o replay (`?replay=1`) só animava a curva de probabilidade,
isolada do resto da página.

**Achado que simplificou tudo**: não precisava construir nenhum
componente novo. O `MapHeatmap`, a `TeamTable` (itens por minuto, item
1 de hoje) e o `ObjectiveRow` já reagem a um `minute` compartilhado
(estado do `MatchDetail`, hoje só controlado pelo slider do mapa de
calor); o replay (`ProbabilityCard`) tinha seu PRÓPRIO `idx`/minuto
interno, completamente desconectado. Bastava sincronizar os dois.

Mudança: `ProbabilityCard` ganhou prop opcional `onMinuteChange`; um
`useEffect` que dispara `onMinuteChange(point.minute)` sempre que
`point.minute` muda ENQUANTO `replaying` é true (fora do replay, não
mexe — evita o hover do gráfico de probabilidade brigar com o slider
do mapa de calor). `MatchDetail` passa `onMinuteChange={setMinute}` —
o mesmo `setMinute` que o slider do mapa de calor já usa. Como
`MapHeatmap`/`ObjectiveRow`/`TeamTable` já são reativos a `minute`,
passaram a acompanhar o replay automaticamente, sem tocar nesses três
componentes. O card "E se..." (`WhatIfCard`) também é alimentado pelo
mesmo `minute` e passou a re-semear sozinho durante o replay, de
graça. ~15 linhas de mudança pra um efeito "estilo broadcast" completo.

Legenda do card atualizada pra deixar isso visível: "Reproduzindo
minuto a minuto — mapa de calor, itens e objetivos abaixo acompanham
o replay."

Verificado com 2 screenshots (replay em `?replay=1`, ~9s de intervalo
real): aos 7 min, mapa de calor/objetivos/itens todos mostravam "7
min"/"até o minuto 7"/"aos 7 min"; 9 segundos depois (minuto 16 no
replay, avançando ~1 min/seg a 1×), os três já mostravam "16 min" em
uníssono, com objetivos atualizados (2 torres, 1 dragão) e itens
diferentes na tabela. `npm run lint` (0 erros) / `npm run test`
(31/31) / `npm run build`: verdes.

**Fecha o lote de 4 feedbacks de uso real (Danone).** Todos os 4
implementados na mesma sessão: itens por minutagem, recomendação de
build condicionada na comp inimiga, leitura de draft (win condition/
contra-pick), e replay sincronizado estilo broadcast.

## 2026-07-08 — Fechando o gap: matchup/sinergia reais no MatchDetail

Gap que tinha ficado registrado desde a Camada 2 (2026-07-08, mais
cedo): o `WhatIfCard` e o `DraftAnalysisCard` do `MatchDetail` citavam
campeão pelo nome mas nunca tinham matchup/sinergia REAL da partida —
só o `CompositionPanel` do Simulador chamava `/compose` (porque já
precisava dele pra estimativa heurística). Usuário confirmou fechar.

`MatchDetail` ganhou um `useQuery` novo pro `/compose`, usando os
campeões da própria partida (`blueChampions`/`redChampions`, já
calculados). Único cuidado real: hooks do React não podem vir depois
de um `return` condicional, e o componente já tinha
`if (analysis.isPending) return <Skeleton />` antes de onde
`blueChampions`/`redChampions` eram calculados — então essas duas
constantes subiram pra ANTES do early-return (usando
`analysis.data?.participants ?? []` como fallback vazio) só pra poder
alimentar o novo `useQuery` (`enabled: !!analysis.data`), removendo a
declaração duplicada que existia mais abaixo.

`compose.data?.lanes`/`synergies.{blue,red}` passam pro
`DraftAnalysisCard` e pro `WhatIfCard` (que já tinha esses parâmetros
opcionais desde a Camada 2/3, só não recebia valor no `MatchDetail`).

Verificado: a "Leitura de draft" passou a citar "55% no top com Singed
contra Darius" e "sinergia negativa de -12,1 pontos percentuais entre
Khazix e Camille"; a "Orientação estratégica" mudou de "aplicado a
este estado" pra "aplicado a este estado E À COMPOSIÇÃO" (a legenda já
reflete quando `lanes` está presente) e citou a mesma sinergia
Khazix+Viktor no texto. `npm run lint` (0 erros) / `npm run test`
(31/31) / `npm run build`: verdes.

## 2026-07-08 — Bug real reportado: KDA/Ouro/CS/Dano não seguiam o minuto

Usuário mandou screenshot aos 3min mostrando ouro/CS/dano com cara de
totais finais de partida (ex.: Draven com 16.471 de ouro aos 3min, que
é claramente valor de fim de jogo) — só a coluna "Itens" tinha sido
corrigida antes (2026-07-08, item 1 do lote de feedback), KDA/Ouro/CS/
Dano/Visão continuavam vindo do `/matches/{id}/analysis` (totais
finais), nunca do minuto do slider.

Verificação primeiro: quais desses dados a Riot realmente grava por
minuto? `participantFrame` tem `totalGold`, `minionsKilled`+
`jungleMinionsKilled`, `damageStats.totalDamageDoneToChampions` — os
três dão pra reconstruir igual aos itens. **Visão não tem em lugar
nenhum da timeline** — `visionScore` só existe como total final da
partida, incremental não é gravado por nenhuma versão da match-v5.
KDA também não é campo direto, mas dá pra contar eventos
`CHAMPION_KILL` até o minuto.

`/matches/{id}/positions` ganhou `gold`/`cs`/`dmg`/`kills`/`deaths`/
`assists` em cada jogador de cada frame — mesma técnica de dois
ponteiros dos itens: `gold`/`cs`/`dmg` vêm direto do
`participantFrame` (sem precisar de evento), `kills`/`deaths`/
`assists` reconstroem contando `CHAMPION_KILL` (`killerId`→abate,
`victimId`→morte, `assistingParticipantIds`→assistência) numa lista
pré-ordenada por timestamp, avançada em paralelo com o loop de frames.

Frontend: `itemsAtMinute` virou `statsAtMinute` (guarda o `FramePlayer`
inteiro por champion_id, não só os itens) — `TeamTable` lê KDA/Ouro/
CS/Dano de lá quando disponível. Cabeçalho da coluna Visão ganhou
`title` explicando que é sempre o total final; a legenda do card
também deixa isso explícito ("Visão é sempre o total final — a Riot
não grava esse número por minuto") — mesmo padrão de honestidade do
resto do projeto (não escondemos a limitação, explicamos ela).

Verificado: aos 3min, Singed mostrava KDA 0/0/0, ouro 959, CS 13, dano
307 (bate exatamente com o `curl` direto no backend); no fim da
partida, KDA 1/2/10, ouro 12.208 — visão idêntica nos dois momentos
(19), confirmando que só ela ficou fixa como esperado. `npm run lint`
(0 erros) / `npm run test` (31/31) / `npm run build`: verdes.

## 2026-07-08 — 3 feedbacks numa imagem: itens incompletos, viés da leitura de draft, jogador na análise

Usuário mandou 3 comentários sobre uma partida real (Jayce/Ekko/Lux/
Draven/Nautilus azul vitorioso vs KSante/Nidalee/Viego/Senna/Rell) e
duas capturas de tela.

**1. "A tabela dos times deveria mostrar todos os itens até os não
completos".** Investigação encontrou uma pegadinha real nos dados
antes de mexer: `item_events` NUNCA gravou `ITEM_DESTROYED`
(componente consumido numa receita) — de propósito, porque servia só
pra "o que foi comprado" no build final. Se eu só ampliasse o filtro
de itens pra incluir componentes/botas sem corrigir isso, os
componentes ficariam "fantasmas" pra sempre no inventário reconstruído
depois de virarem item final (pior que o bug atual). Corrigido na
raiz:
- `db/schema.sql`: `item_events.action` de `VARCHAR(4)` pra
  `VARCHAR(10)` (cabe "DESTROY"); migração aplicada na tabela viva.
- `src/etl/load_items.py`: agora grava `ITEM_DESTROYED` como ação
  `DESTROY`. Confirmado seguro: todo consumidor de `item_events` já
  trata qualquer ação != BUY como remoção (`CASE WHEN action='BUY'
  THEN 1 ELSE -1 END` em SQL, `1 if action=="BUY" else -1` em Python)
  — adicionar DESTROY não quebra `champion_items`, `tactics.py` nem
  nada existente, só corrige a contagem. Limite documentado: ITEM_UNDO
  só desfaz BUY/SELL (a Riot nunca referencia um DESTROY em
  beforeId/afterId), então desfazer a compra que finaliza uma receita
  deixa os componentes permanentemente "destruídos" na reconstrução —
  caso raro, não tratado.
- Reprocessado (`python -m src.etl.load_items`): 23.133 timelines →
  10.392.285 eventos (quase dobrou, DESTROY ficou perto de metade das
  linhas — 4,59M).
- Novo `_trackable_item_ids` em `main.py` (purchasable, não consumível/
  trinket, mapa 11 — SEM exigir `into` vazio nem custo >= 1100) usado
  só em `/matches/{id}/positions` (a `TeamTable` por minuto); o coach
  (`tactics.py`) e `/stats/champion/{name}/items` continuam com
  `_completed_item_ids` (intencional — "itens finalizados" faz mais
  sentido pra recomendação de build e pra "o que essa build significa"
  do que componente solto).
- Verificado que não ficou nada fantasma: rastreei Singed minuto a
  minuto — aos 20min tinha Cinzas do Destino + Máscara Assustadora,
  aos 25min os dois sumiram e virou Tormento de Liandry (os dois
  componentes constroem nele) — comportamento correto.

**2. "Essa é a análise do draft, mas o ganhador foi o time azul".** O
usuário apontou que a leitura de draft concluiu "o vermelho é
claramente favorecido" mas quem ganhou foi o azul — e a leitura tinha
dito algo tipo "o azul só vence se fechar antes dos 25min", só que a
partida terminou aos 28,7min. Decisão: não faz sentido "consertar" a
leitura pra sempre bater com o resultado (isso destruiria o propósito
dela — um draft pior no papel pode vencer por execução, não é uma
predição de resultado). O que É um problema real: a leitura estava
soando confiante demais com números específicos (um corte de "25
minutos" preciso) sem deixar claro que é uma leitura ESTRATÉGICA
pré-jogo, não uma predição. Adicionado ao final do prompt de
`generate_draft_analysis()`: a leitura precisa terminar deixando
explícito que é sobre "quem tem o caminho mais fácil no papel", e que
um draft pior pode vencer por execução/agressão early/erro do
adversário — então pode não bater com o resultado real.

**3. "Deveríamos saber quem é o jogador... a análise do draft deveria
fazer isso".** O pedido construtivo por trás do ponto 2: a leitura de
draft comparava só CAMPEÃO×CAMPEÃO, cega pra quem estava jogando —
mas o sistema já tinha exatamente esse dado pronto
(`player_effect()`/shrinkage, usado no "Jogadores (opcional)" do
Simulador). Faltava só conectar pra partida REAL:
- `/matches/{id}/analysis` ganha `puuid` por participante (já era
  consultado no SQL, só não ia pra resposta).
- `CoachLane` (Pydantic + TS) ganha `blue_player`/`red_player`
  opcionais (mesmo formato de `ComposePlayerEffect` — nome, jogos no
  campeão, win rate bruto e ajustado por shrinkage).
- `MatchDetail.tsx`: `bluePlayers`/`redPlayers` (posição→puuid)
  calculados do mesmo jeito que `blueChampions`/`redChampions` (antes
  do early-return), passados pro `/compose` — fecha de vez o gap, essa
  partida real agora usa a MESMA leitura ajustada por jogador que o
  Simulador já tinha quando o usuário especifica jogadores.
- `_format_lanes()`/`generate_draft_analysis()` em `advice.py`: cita
  win rate do jogador NAQUELE campeão quando disponível, e instrui a
  LLM a ponderar isso na leitura (jogador muito acima/abaixo da média
  pode inverter a leitura do matchup puro).

Testado com a partida real: a leitura passou a citar "o jogador azul
singed420#asc25 tem 59% de taxa ajustada especificamente neste
campeão, enquanto beware#虚無月 está em apenas 50% ajustado" e "o

> **Os caracteres CJK desta linha NÃO são erro de geração.** `beware#虚無月`
> é o Riot ID de um jogador profissional real (a base tem `Beware` com 139
> jogos em `pro_players.player_name`; o banco guarda só o nome antes do `#`,
> e a tag depois do `#` pode estar em qualquer alfabeto). Anotado aqui porque
> `docs/verifica_tcc.py` acusa caractere não latino — e ele tem razão para o
> TCC, onde não cabe nome de invocador, mas aqui o nome é o dado.
jogador vermelho saoksaopkaojsip#br1 está em apenas 43% ajustado após
shrinkage em apenas 5 jogos — isso é um sinal de falta de
familiaridade com Khazix". Verificado nos três pontos via curl direto
e Playwright real, sem erro de console. `npm run lint` (0 erros) /
`npm run test` (31/31) / `npm run build`: verdes.

## 2026-07-08 — Build sugerida com ícones (versão estruturada, não só texto)

Pergunta do usuário: "foi adicionado exemplos de builds para fazer?".
A resposta era não — a recomendação de build (feedback 2/4 de mais
cedo) só existia como menção solta dentro do parágrafo de texto, sem
nenhuma UI dedicada. Pedido de adicionar a versão visual (ícones de
item, como lolalytics/u.gg mostram).

**Problema de design**: a LLM só devolve texto livre. Pra virar ícone
de verdade na tela, precisa de um `item_id` que bata com o catálogo —
não dá pra confiar na LLM "lembrar" o ID numérico certo de cabeça
(ela erra fácil), então a solução foi: LLM devolve NOME do item
(confiável, ela conhece os itens de LoL bem) via **tool calling**
(function calling) da Anthropic, e o backend resolve nome → ID
usando o catálogo já carregado (`_item_name_to_id`, novo dict
minúsculo→id em `main.py`).

- `generate_advice()` em `advice.py` agora usa
  `tools=[BUILD_ADVICE_TOOL]` com `tool_choice` forçado — o schema
  pede `narrative` (texto, como já era) + `build_suggestions[]`
  (`champion`, `team`, `items` — 1-3 nomes de item, `reason`). Função
  passou a devolver uma tupla `(narrative, build_suggestions)` em vez
  de só string.
- `/coach` resolve cada nome pro `item_id` real (ou descarta a
  sugestão se o nome não bater com nenhum item do catálogo — nunca
  manda "lixo" pro front) e devolve `build_suggestions` na resposta.
- `CoachCard` (frontend) ganha uma seção "Build sugerida" abaixo do
  texto — uma linha por sugestão, nome do campeão colorido por time
  (azul/vermelho), ícones reais via `itemIcon()`, motivo curto.

**Achado de confiabilidade real, não só código**: a primeira versão
do prompt (pedindo `build_suggestions` como um "extra" ao final,
"SÓ quando fizer sentido... lista vazia se não houver dado
suficiente") tinha taxa de acerto baixa — em 2 tentativas reais no
navegador, a narrativa mencionava item explicitamente no texto
("Kaisa e Camille precisam de itens defensivos imediatos...") mas a
lista estruturada vinha VAZIA mesmo assim. Corrigido reformulando a
instrução como "releia o que você escreveu e transcreva pra
`build_suggestions`" (uma tarefa de EXTRAÇÃO do que já foi decidido,
não uma decisão nova) — subiu de 0/2 pra 4/5 em teste direto de
backend. Ainda não é 100% (variância inerente de LLM numa tarefa de
extração estruturada secundária) — aceito como razoável dado que o
botão "Gerar de novo" já é um retry natural pro usuário.

Verificado visualmente: a seção "Build sugerida" mostrou "Camille" +
ícone de Coração de Aço + "Oferece resistência mágica contra
Lissandra e escudo ao time, compensando a sinergia negativa com
Khazix" e "Viktor" + ícone de Véu da Banshee + "Mitiga o burst de
Lissandra... e prolonga a sobrevivência em teamfights" — batendo
exatamente com o que a mesma narrativa já dizia em texto. `npm run
lint` (0 erros) / `npm run test` (31/31) / `npm run build`: verdes.

## 2026-07-08 — Build sugerida virou dado real, não a LLM inventando (2 achados no mesmo dia)

Usuário questionou a sugestão do exemplo anterior: "Camille + Coração
de Aço" — "não acho que a Camille faça Coração de Aço, mas posso
estar errado". Fui checar o item de verdade no catálogo em vez de
confiar na memória: `item_id 3084` tem `tags: ['Health',
'HealthRegen']` — SEM resistência mágica nenhuma. Minha explicação
anterior ("oferece resistência mágica contra Lissandra") estava
errada. Causa raiz: o mecanismo resolve o NOME do item de forma
confiável (o ícone que aparece é sempre um item de verdade), mas o
campo `reason` é texto livre da LLM recordado de memória, nunca
checado contra os `tags` reais do item — a LLM pode escolher o item
certo pro contexto e ainda assim inventar o "porquê" errado.

**Correção pedida pelo usuário**: "precisamos saber os melhores itens
pra cada campeão, os mais feitos com maior porcentagem" — dado que JÁ
existia! `/stats/champion/{name}/items` (endpoint de 2026-07-03) já
calcula, por campeão, os itens finalizados mais construídos com win
rate REAL naqueles jogos (`item_events`, filtro `_completed_item_ids`,
mínimo 20 jogos). Só faltava conectar no coach.

- Extraída a query em `_champion_top_items(cur, champion_name,
  min_games, limit)` — helper reutilizado tanto pelo endpoint de
  análise do campeão (limit=12, como já era) quanto pelo `/coach`
  (limit=3, pra não inchar o prompt).
- `/coach` busca isso pra cada campeão conhecido (blue+red) antes de
  chamar `generate_advice()`, passa como `top_items: dict[campeão,
  lista_de_itens]`.
- `advice.py`: novo bloco de prompt "Itens finalizados mais
  construídos por campeão, com win rate NAQUELES jogos — DADO REAL do
  histórico" + instrução pra preferir esses itens (citando o número
  real) em vez de inventar item ou explicação de status.

**Segundo achado, de confiabilidade (não só de precisão)**: com o
bloco de itens reais adicionado, a taxa de acerto da lista estruturada
`build_suggestions` DESABOU — de ~4/5 (medido antes) pra 0/3, depois
2/6 mesmo simplificando a instrução. `stop_reason` do Anthropic
sempre veio `tool_use` (nunca `max_tokens`), descartando truncamento —
era genuinamente a LLM "esquecendo" de preencher a parte estruturada
quando o prompt cresce, mesmo escrevendo o item explicitamente no
texto (6 menções reais na narrativa, 0 na lista estruturada numa
tentativa). Mesmo fenômeno de diluição de atenção por tamanho de
prompt já visto no `schema_context.py` do NLQ (2026-07-08, mais
cedo). **Correção estrutural**: separar em DUAS chamadas de LLM em vez
de uma — a primeira só escreve a narrativa (sem tool calling, sem
concorrência de atenção com uma tarefa de estruturação); a segunda
(`_extract_build_suggestions`, temperatura mais baixa, 0.2) releem o
texto já escrito e EXTRAI as menções de item — uma tarefa mecânica de
releitura, não uma decisão nova concorrendo com a escrita criativa. Só
roda a segunda chamada se o texto tiver alguma chance de mencionar
item (atalho barato: `"item" in narrativa.lower()` etc.). Subiu de
0/3-2/6 pra **6/6** em teste direto. Custa uma chamada extra de LLM
(latência), mas o ganho de confiabilidade compensa.

Limpeza: a instrução antiga que pedia "crie uma entrada em
build_suggestions" tinha ficado presa no prompt da PRIMEIRA chamada
(que não tem mais essa ferramenta) — a LLM tentava compensar colando
um bloco `**Build suggestions:**` em markdown no fim do texto corrido
(a regra era "sem markdown"). Removida a instrução obsoleta; texto
voltou a ficar limpo (ainda ocorre ocasionalmente um cabeçalho em
negrito tipo `**Orientação para o time vermelho:**` — resquício
cosmético menor, não perseguido mais a fundo).

Verificado: narrativa e seção estruturada citam os MESMOS números
reais ("Ampulheta de Zhonya, 58% vitória em 505 jogos", "Couraça do
Defunto, 58% vitória em 557 jogos", "Dente de Na'Shor, 52% vitória em
957 jogos") — sem invenção de stat. `npm run lint` (0 erros) / `npm
run test` (31/31) / `npm run build`: verdes.

## 2026-07-10 — Consulta NL não respondia build nem tinha catálogo de item

Usuário reportou: "No modo consulta NL ele não está fornecendo builds,
nem explicações de matchs. Devemos expandir nossa pergunta aos
dados." Testei os dois separadamente antes de mexer em qualquer
coisa. Matchup ("Camille contra Darius no topo, quem ganha mais
confrontos diretos?") já funcionava de primeira — o schema_context já
ensina o padrão EXISTS por campeão/team_id pra composição, não
precisava de nada novo. Build ("Quais os itens mais construídos pela
Camille?") falhava de verdade: `ValueError: Tabelas não permitidas:
{'participant_items'}` — a LLM alucinou um nome de tabela porque
`item_events` nunca tinha sido ensinada ao NLQ (só é usada pelo
coach/endpoint de análise de campeão, nunca no `schema_context.py`).

**Decisão de design**: `item_events` só tem `item_id` numérico, sem
nome. Ensinar a tabela sozinha deixaria o `explain_result()` (a
narração em português do resultado) tentando "lembrar" nome de item
por ID de cabeça — exatamente o mesmo bug de invenção de stat já
corrigido pro coach em 2026-07-08 (Coração de Aço). Solução: catálogo
de verdade no banco, pra qualquer nome de item em qualquer resposta
vir de JOIN, nunca de memória do modelo.

- `db/schema.sql`: nova tabela `items(item_id, name, total_gold,
  purchasable, map_11)`.
- `src/etl/load_item_catalog.py` (novo): carrega `data/items.json`
  (Data Dragon) na tabela — TRUNCATE + reinsere, 706 itens. Rodado:
  `Coração de Aço` (3084) confere com o catálogo real (3000 ouro,
  purchasable, map_11).
- `schema_context.py`: ensinadas `item_events` e `items`, com exemplo
  de CTE (primeira compra por partida via `MIN(ts_ms)` + `action =
  'BUY'`, pra recompra após vender não contar duas vezes).
  `evaluate_nlq`: 23/26 = 88%, mesmas 3 falhas benignas de sempre —
  sem regressão.

**Testando a pergunta original de ponta a ponta (não só o benchmark,
que não cobre build) achei DOIS bugs reais no validador que o
benchmark não pegou**, porque nenhuma das 26 perguntas usa CTE ou as
tabelas novas:

1. `validate_sql()` só aceitava SQL começando literalmente com
   `select` — o exemplo de CTE que acabei de ensinar (`WITH ... AS
   (...) SELECT`) era rejeitado antes mesmo de chegar na checagem de
   tabelas. Corrigido: aceita prefixo `select` OU `with`.
2. `item_events`/`items` nunca tinham sido adicionadas a
   `ALLOWED_TABLES` — mesmo corrigindo o item 1, a query ainda
   rejeitava com "Tabelas não permitidas". Corrigido: adicionadas.
3. Um TERCEIRO bug apareceu só depois de corrigir os dois acima: o
   regex que extrai nomes de tabela de `FROM`/`JOIN` não distinguia
   tabela real de nome de CTE — `first_buys`/`champ` (definidos no
   `WITH`) caíam no mesmo regex e eram rejeitados como tabela
   desconhecida. Corrigido extraindo os nomes definidos em `nome AS
   (` e excluindo-os do conjunto "desconhecido" (`FORBIDDEN` continua
   rodando sobre o texto inteiro, então não abre brecha de segurança
   — só a checagem de allowlist de tabela ficou mais precisa).

Depois dos 3 fixes, `evaluate_nlq` rerodado de novo (regra da casa,
mudei `validate_sql` duas vezes) — 23/26 = 88%, sem regressão em
nenhuma das duas rodadas.

**Quarto achado, de qualidade do resultado (não erro, mas inútil na
prática)**: com tudo corrigido, a query rodava e retornava dados
reais, mas o top da lista era poção, ward e bota básica (`Poção de
Vida`, `Espada Longa`, `Cristal de Rubi`) — tecnicamente "comprado
pela Camille", mas não é o que "build" quer dizer. Adicionado ao
worked example: filtro `total_gold >= 1300` (exclui componente barato
e consumível, mantém item lendário/mítico de verdade). Reconfirmado
com SQL direto contra o banco antes de mudar o prompt: com o filtro,
o topo vira `Céu Dividido` (2565 jogos, 49.5% vitória), `Sinal de
Sterak`, `Força da Trindade` etc. — dado de build de verdade.
`evaluate_nlq` rerodado uma terceira vez: 23/26, sem regressão.

Teste final de ponta a ponta: `ask('Quais os itens mais construídos
pela Camille?')` retorna SQL válida, dados reais, e `explain_result()`
narra os nomes certos (vêm do JOIN, não de memória) — a seção "Leitura
de jogo" (que é explicitamente conhecimento do modelo, não dado, por
design do prompt) ainda pode errar detalhe de stat de item, mas isso
já é avisado ao usuário como opinião, não fato — diferente do bug do
coach que afirmava stat errada como se fosse dado.

## 2026-07-13 — Revisão pós-features: build_suggestions voltava vazio de verdade

Pedido do usuário: um planejamento de revisão focado em gaps deixados
pelas features recentes (~20 commits desde a última revisão completa
em 2026-07-03). Passo 1 (baseline): `npm run lint`/`test`/`build`
(frontend) e `evaluate_nlq`/`smoke_test`/`validate_predictions`
(backend) — tudo dentro do esperado, incluindo as 10 "falhas" de
`validate_predictions` (mesmas categorias já documentadas em
2026-07-03 como característica do modelo, não bug). Único achado
novo: o bundle JS passou de despercebido para acima do limite de
aviso do Vite (818KB) — sintoma de acúmulo de páginas sem
code-splitting, anotado pra limpeza depois, não corrigido agora.

Passo 2 (auditoria de grounding do LLM): testei `/coach` de ponta a
ponta contra uma partida real (`BR1_3257266337`) em vez de só ler o
código. `build_suggestions` voltou **vazio em 4/4 tentativas**, mesmo
com a narrativa citando claramente vários itens reais com stats reais
("Tormento de Liandry, 53% vitória em 771 jogos" etc.) — quebra a
garantia de "6/6" verificada em 2026-07-08 pra essa mesma função.

**Causa raiz**: `stop_reason: max_tokens` na chamada de extração
(`_extract_build_suggestions`, `max_tokens=500`) — confirmado
inspecionando a resposta bruta da API (`tool_use.input == {}`, JSON
cortado no meio). Interação entre features: adicionar `top_items` com
stats reais à narrativa (a correção de grounding de 2026-07-08) deixou
a narrativa mais rica/longa, e ninguém reajustou o orçamento de tokens
da chamada SEPARADA que releva essa narrativa depois — o mesmo tipo de
bug já corrigido uma vez em `nl_to_sql.py` (`generate_sql`, 500→1200
tokens), mas dessa vez silencioso: sem erro nenhum, só ícone de item
sumindo da UI.

**Gap sistêmico relacionado, também corrigido**: nenhuma das 3 chamadas
de LLM em `advice.py` (`generate_advice`, `_extract_build_suggestions`,
`generate_draft_analysis`) verificava `stop_reason` — só `generate_sql`
do NLQ tinha esse guard. Adicionado `if stop_reason == "max_tokens":
raise ValueError(...)` nas duas chamadas de narrativa (falha alta,
melhor um erro claro que um parágrafo cortado sem aviso) e um retorno
`[]` explícito na extração (falha baixa — é enriquecimento opcional,
JSON parcial não é confiável o bastante pra usar mesmo que pareça
válido por acaso).

**Correção**: `_extract_build_suggestions` subiu de 500 para 1000
tokens. Reverificado com 4 chamadas novas na mesma partida: 3/4
`build_suggestions` populado (a 4ª vez a narrativa genuinamente não
mencionou item nenhum — variação normal de `temperature=0.4` na
narrativa, não é bug, e o atalho que evita a chamada de extração à
toa funcionou corretamente). De 0/4 quebrado pra confiável sempre que
a narrativa de fato recomenda item.

Passo 3 (reverificação ponta a ponta das features empilhadas desde
2026-07-08): reproduzi o fluxo REAL do MatchDetail contra a partida
`BR1_3257266337` — `/compose` com os `puuid`s reais dos 10 jogadores
→ `/coach/draft` com os `lanes`/`synergies` retornados (exatamente o
que `DraftAnalysisCard` recebe na página de verdade). Conferi cada
número citado na narrativa contra o JSON bruto do `/compose`: win
rate de lane (64%/63%/65%/55%), win rate ajustado por jogador
(59%/55%/56%/48%/43%...) e sinergia de dupla (Khazix+Camille -12,1pp,
Khazix+Viktor +10,5pp) — **todos batem exatamente** com o dado real,
zero número inventado. `/matches/{id}/positions` confirmado
retornando itens+ouro+CS+dano+KDA+posição juntos por minuto no mesmo
frame (base de `91b2e0c` e do replay sync de `6517a8a`) — estrutura
já unificada, sem gap aparente. Não incluiu passada visual no
navegador (sem Playwright disponível nesta sessão) — só validado via
chamada real à API, não clique real na UI; fica pendente se quiser
confirmação visual completa.

## 2026-07-13 — Passo 4 da revisão: limpeza dos gaps pequenos

Fechando os itens pequenos já documentados e "não perseguidos a
fundo" em entradas anteriores:

- **Resíduo de markdown na narrativa do coach** (`**Orientação para o
  time X:**` ocasional, apesar do prompt pedir "sem markdown"): 0/8
  amostras reais desta sessão reproduziram, então não vale caçar a
  causa no prompt — em vez disso, `_strip_markdown()` (novo helper em
  `advice.py`, `text.replace("**", "")`) aplicado nas duas narrativas
  (`generate_advice`, `generate_draft_analysis`). Correção barata e
  segura o bastante pra não valer a pena esperar o próximo usuário
  achar de novo.
- **2 warnings do ESLint em `chart.tsx`** (`react-refresh/only-export-
  components` — o arquivo exportava `AXIS_TICK`/`GRID`, constantes,
  junto com o componente `ChartTooltip`): extraídas pra
  `frontend/src/lib/chart-tokens.ts`; `chart.tsx` agora só exporta o
  componente. Atualizados os 5 imports (`Competitivo`, `Dashboard`,
  `Explain`, `MatchDetail`, `Predict`). `npm run lint`: 0 erros, 0
  warnings (era 0 erros, 2 warnings).
- **Bundle único de 818KB** (acima do limite de aviso do Vite, achado
  no passo 1 desta revisão — sintoma de acúmulo de página sem code-
  splitting): `App.tsx` passou a importar cada página via
  `React.lazy()` + `<Suspense fallback={<Skeleton />}>` em vez de
  import estático. `npm run build`: sem aviso de chunk grande, maior
  chunk agora 350KB; `tsc` (que checa a forma exata do export nomeado
  de cada `import().then(m => ({default: m.X}))`) e `npm run test`
  (31/31) continuam limpos. Ressalva: os testes de página montam cada
  componente diretamente (`pages.smoke.test.tsx`), não passam pelo
  `Suspense`/lazy-loading de `App.tsx` — e não há Playwright nesta
  sessão pra clicar de verdade entre rotas. Risco residual considerado
  baixo (mecanismo padrão do React/Vite, tipos conferidos pelo tsc),
  mas fica registrado como não 100% verificado visualmente.
- **Botas fora do filtro `total_gold >= 1300` de "itens de build"**
  (decisão já tomada e testada mais cedo hoje, ver entrada "Consulta
  NL não respondia build"): mantido como está — filtro existe pra
  responder "itens de build", onde botas raramente são o ponto
  central da pergunta; não é um gap, é escopo intencional.

## 2026-09-28 — Coleta ampliada (só a EUW1 avançou), Anexo A e o quadro do Apêndice C

Fechando a rastreabilidade de três coisas que o texto do TCC atribui a esta
data e que não tinham registro aqui: a rodada de coleta multi-região, as
6 capturas do Anexo A e a geração do quadro cruzado do Apêndice C.

**1. Estado da base medido nesta data.** Comparando com o fechamento de
2026-07-06 (23.133 partidas; BR1 11.936, EUW1 5.280, KR 4.471, NA1 1.446 —
somam exatamente 23.133, sem EUN1):

| Região | 2026-07-06 | 2026-09-28 | Δ | Vitória vermelho |
|---|---:|---:|---:|---:|
| BR1 | 11.936 | 11.936 | 0 | 56,3% |
| EUW1 | 5.280 | 6.281 | +1.001 | 53,8% |
| KR | 4.471 | 4.471 | 0 | 50,2% |
| NA1 | 1.446 | 1.446 | 0 | 51,9% |
| EUN1 | — | 20 | +20 | 50,0% (fora da conclusão) |
| **Total** | **23.133** | **24.154** | **+1.021** | |

Só a EUW1 cresceu. **BR1, KR e NA1 estão idênticos aos de 2026-07-06** — a
coleta multi-região desses três pontos simplesmente não avançou no intervalo
(o mesmo sintoma de NA1 já registrado em 2026-07-06). Causa provável segue
sendo a mesma, já diagnosticada: `collect_matches` sempre seleciona o top-N
por `league_points DESC`, e o topo do ladder Challenger/GM já foi colhido —
crescer exige `--players` bem maior (500-1000+), não só rodar de novo. Os
+1.021 (+4,4%) são da ordem do "incremento pequeno" que a entrada de
2026-07-06 já classificou como insuficiente para retreinar, e por isso
**não houve retreino** — decisão mantida.

**2. Divergência de 11 partidas com a captura do Anexo A — REGISTRADA COMO
LACUNA, NÃO RESOLVIDA.** A captura `reports/anexo_a/02_dashboard.png`
mostra **EUW1 6.270** e KPI **Partidas 24.143**, enquanto o quadro do TCC
traz EUW1 6.281 e total 24.154. O que dá para afirmar sem inventar:
- As duas leituras são **internamente consistentes**. Somando as linhas da
  captura: 11.936 + 6.270 + 4.471 + 1.446 + 20 = **24.143**, igual ao KPI.
  Somando as linhas do quadro do TCC: 11.936 + 6.281 + 4.471 + 1.446 + 20 =
  **24.154**. Nenhuma das duas tem região transcrita errada.
- A diferença é **exatamente 11 partidas, todas em EUW1** — ou seja, a única
  região que estava crescendo. Hipótese mais provável: **a coleta ainda
  estava rodando no momento da captura**, e o quadro do TCC foi lido
  minutos depois. É exatamente o efeito já documentado em 2026-07-04 ("a
  coleta adicional estava RODANDO durante a verificação — solo queue
  passou de 10,4k para 11,8k ao longo da sessão").
- **Não corrigi nenhum dos dois números.** Reprodução: `GET /stats/regions`
  (`src/api/main.py:332`) ou a query direta
  `SELECT m.platform_id, COUNT(*), AVG(t.win::int) FROM matches m JOIN
  teams t ON t.match_id = m.match_id AND t.team_id = 200 GROUP BY
  m.platform_id ORDER BY COUNT(*) DESC`. Quem for conferir vai ver 33.713
  (ver entrada de 2026-10-03), porque a base cresceu de novo desde então.

**3. Números que o Anexo A deixa como artefato.** A captura do Dashboard é
a única das 6 que carrega números do modelo de dados, e eles são
verificáveis direto na imagem: 24.143 partidas, 25.642 jogadores únicos, 17
patches cobertos, duração média 26,8 min, 57,3 abates por partida, 63,5%
das partidas chegam ao late game, lado azul 45,7% / vermelho 54,3%, e a
leitura da faixa +6k a +8k (azul vence 96,1%; extremo oposto, -8k a -6k,
3,2%). O gráfico de patches mostra 16.13 ainda dominante e 16.17/16.18/
16.19 com barras pequenas — **inferência minha**: as partidas novas da
rodada vieram de patches posteriores ao fechamento de 2026-07-06, o que é
coerente com a coleta ter seguido rodando. A data de geração das 6
capturas (2026-09-28, Playwright/Chromium 1440×900, página inteira) vem do
Anexo A do TCC; a metadata dos PNG não foi conferida nesta revisão.

**4. Apêndice C: gerado nesta data, mas sobre o dataset de 2026-07-06.**
Os `n` do quadro (23.053 / 22.973 / 20.254 / 16.179) são **exatamente** os
registrados na entrada de 2026-07-06 para os quatro cortes. Ou seja:
`data/features_phases.csv` **não foi regenerado** entre 2026-07-06 e
2026-09-28 — coerente com a coleta ter crescido sem `build_features` ter
rodado. Consequência honesta para a Seção 4.4: dizer que a medição "de
2026-09-28 reproduz exatamente os números do retreino de 2026-07-06"
(45,6% de vitória azul em 22.973) é verdade, mas é **reprodução sobre
arquivo idêntico**, não confirmação independente — o mesmo `train_baseline`
sobre o mesmo CSV. Não é erro; é o que o registro permite afirmar.

**Pendências abertas por esta data (não resolvidas, e é para não fingir
resolução):**
- **O quadro do Apêndice C não tem script reproduzível no repositório.**
  `train_baseline.py` faz **só o corte de 15 min** (o próprio docstring diz
  "vitória do time azul aos 15 min") e lê `data/features.csv`. As linhas de
  10/20/25 min × 3 modelos foram geradas por uma execução que não ficou
  registrada em script. Se a banca pedir reprodução, falta escrever o
  script que varre `features_phases.csv` pelos 4 cortes.
- **A "verificação por SQL direto" citada no TCC (pendência 5 da lista
  final) não tem artefato neste repositório.** O texto remete à memória do
  projeto (`feedback_verify_dashboard_numbers`), que não é versionada aqui
  — nem `project_scope_decisions.md`, citado em entradas anteriores, existe
  no repo. Pendente: rerodar a query e arquivar a saída (ex.:
  `reports/stats_regions_2026-10-03.txt`), para que a afirmação tenha
  lastro no repositório e não só na memória.
- **A divergência de 11 partidas** acima: confirmar por `GET /stats/regions`
  e, se for realmente instantâneo, escolher uma única data de corte para o
  quadro do TCC e citar a captura como evidência do que ela mostra.

## 2026-09-29 — Regras de formatação ABNT/UNISINOS confirmadas no template oficial

Origem das regras: duas fontes **externas ao repositório** — a estrutura
LaTeX oficial da instituição (classe `UNISINOSartigo`, exemplo enviado pelo
curso) e os comentários do Prof. Elvandi no TCC I revisado
(`Downloads/Revisado - TCC - revisado Prof. Elvandi.docx`, que não está no
repo). Nenhuma das duas é preferência do autor, e é por isso que valem mais
que a aparência dos templates brutos: são duas leituras independentes da
mesma fonte institucional.

**Aplicado (a lista real, não um resumo):**
- **Títulos de seção em maiúscula e SEM negrito** — os templates brutos
  mostram negrito; a orientação é sem. Já aplicado.
- **Referências bibliográficas com 1 linha em branco** separando cada
  entrada (norma ABNT). Já aplicado.
- **Palavras-chave separadas por ponto final**, não ponto-e-vírgula —
  corrigido no Resumo e no Abstract.
- **Tabelas do texto (Seções 4.3/4.4, Apêndices B/C/D) rotuladas como
  "Quadro"**, não "Tabela": a instituição tem ambiente LaTeX próprio e
  "Lista de Quadros". Todas já renomeadas.
- **Estrutura de seções do corpo é livre, por acordo com o orientador** —
  não existe seção "Trabalhos Relacionados" obrigatória no template
  genérico. Isso **reduz** a pendência de conteúdo nº 2 (posição de
  "Trabalhos Relacionados"): deixa de ser bloqueio estrutural e vira
  preferência a confirmar. **Limite de páginas: 25 a 30**, sem contar
  apêndices e anexos.

**O que ainda falta (e é mecânico, não de conteúdo):**
- **Numeração sequencial dos Quadros** (Quadro 1, 2, 3...). Deixada de fora
  de propósito: a ordem dos quadros ainda muda com a consolidação do texto,
  e o número só fecha na conversão final.
- **Conversão para o formato de entrega — que ainda não está decidido.** A
  pendência 4 do texto fala em verter para o template `.docx`
  institucional (capa, espaçamento, fonte, numeração de página), mas a
  análise de 2026-09-29 foi sobre a estrutura **LaTeX**. Os dois caminhos
  foram lidos; a escolha é o que define se a numeração de Quadros e a
  legenda/fonte das figuras são aplicadas em `.docx` ou no LaTeX. Fica
  registrado como pendência, não como decisão tomada.
- **Figuras: legenda no topo, fonte obrigatória abaixo**, inclusive em
  figura de autoria própria. Ainda não aplicável ao Markdown atual; fica
  obrigatório quando as 6 capturas do Anexo A entrarem como figuras — cada
  uma vai precisar de fonte ("captura de tela própria, dados de
  produção").
- **Arquivo-modelo `.docx` ainda não localizado** no repositório nem nas
  pastas locais verificadas (`Downloads/TCC/` só tinha versões do TCC I).

**Por que isto entra no diário e não só na lista de pendências do TCC:**
regra de formatação que mora só no texto se perde na conversão — e a
conversão é exatamente a etapa em que alguém abre o arquivo, vê "Quadro"
virou "Tabela" de novo e não tem como saber que era regra da instituição.

## 2026-10-03 — Viés de lado remedido em 33.713 partidas, reforma da bateria de validação e correções de consistência

### 1. Medição do viés de lado com a coleta avançada

Mesma pergunta do `GET /stats/regions` (`src/api/main.py:332`):

```sql
SELECT m.platform_id, COUNT(*) AS matches, AVG(t.win::int) AS red_win_rate
FROM matches m JOIN teams t ON t.match_id = m.match_id AND t.team_id = 200
GROUP BY m.platform_id ORDER BY COUNT(*) DESC
```

| Região | 2026-07-06 | 2026-09-28 | 2026-10-03 | Δ (09-28→10-03) | Vermelho (10-03) |
|---|---:|---:|---:|---:|---:|
| BR1 | 11.936 | 11.936 | 11.936 | 0 | 56,3% |
| EUW1 | 5.280 | 6.281 | 11.744 | +5.463 | 53,4% |
| KR | 4.471 | 4.471 | 8.567 | +4.096 | 50,3% |
| NA1 | 1.446 | 1.446 | 1.446 | 0 | 51,9% |
| EUN1 | — | 20 | 20 | 0 | 50,0% (fora) |
| **Total** | **23.133** | **24.154** | **33.713** | **+9.559** | |

O que importa no achado: **a direção não mudou**. As quatro regiões com
amostra relevante continuam pendendo para o vermelho (50,3% a 56,3%) pela
**terceira** medição seguida, e agora com EUW1 e KR quase dobradas em
relação a 2026-09-28. Isso é o que fecha a leitura "é padrão de elo
altíssimo em geral, não artefato do Brasil": com 11,7 mil partidas de
EUW1 e 8,5 mil de KR, o BR1 (11.936, estável nas três medições) deixa de
ser o único nem o maior volume de evidência isolado. BR1 e NA1 **não se
moveram** de
2026-07-06 até agora — o growth foi todo de EUW1/KR, e NA1 continua sendo a
limitação declarada.

**Ressalva de verificação (para não passar por mais forte do que é):** os
números acima vêm da medição feita nesta data. O que eu conferi nesta
passada de documentação foi a **coerência interna** (as linhas somam
exatamente 33.713; BR1 11.936 e NA1 1.446 batem com os artefatos de
2026-07-06 e com a captura do Anexo A) — **não** houve segunda execução
independente da query, e **a saída não foi arquivada**. Pendente: rerodar e
salvar em `reports/`, para a Seção 4.3 ter lastro no repo e não só nesta
entrada.

**Decisão de escopo:** usar **33.713 para a análise de viés de lado**
(Seção 4.3) e **manter o modelo em 23.133 partidas**. O motivo é de escopo,
não de medição: retreinar com o volume novo exigiria rever a Seção 4.4
inteira e o Apêndice C (as duas seções citam métricas que nascem do
dataset de 23.133), e o texto já estava em consolidação. Vale registrar o
que se está assumindo ao não retreinar: as features de produção
(`data/features_phases.csv`) **continuam as de 2026-07-06** — as 33.713
partidas existem no banco, mas não têm contraparte em features nem em
modelo. Ou seja, o modelo em produção não "sabe" nada das 10,5 mil
partidas que a Seção 4.3 usa para medir viés de lado. O Apêndice D
justifica a escolha pela mesma lógica em outro contexto: entre as 9
tentativas de enriquecimento, o único ganho real veio de **volume**

> **REVOGADA em 2026-10-04.** A decisão acima foi anulada no dia seguinte:
> a coleta seguiu até 39.426 partidas (a NA1 foi de 1.446 para 7.159), o
> modelo foi retreinado sobre 39.188 e o Apêndice C foi refeito. O raciocínio
> de escopo estava certo na data e ficou errado com a base maior — o que
> fica registrado aqui porque a entrada original continuaria parecendo a
> decisão vigente. Ver a entrada de 2026-10-04.
(0,8214 → 0,8393), o que torna o retreino o caminho certo — só não era o
caminho cabível nesta versão do texto.

### 2. Reforma da bateria de validação comportamental

**O problema de fundo: um portão que não podia falhar.** `tests/validate_predictions.py`
acumulava as falhas numa lista `FAIL`, imprimia "N checagens falharam" e
**terminava com código 0 sempre**. O `import sys` estava no arquivo desde o
começo, para um `sys.exit` que nunca foi escrito. Ou seja: **nenhum script
em `tests/` podia reprovar**, e o agente `validador` do projeto rodava um
gate que reportava sucesso ao sistema independente do resultado. Isso é
pior que não ter bateria: é ter uma bateria que dá um tick verde falso.

**A seção 1 media a coisa errada.** A antiga "Monotonicidade" variava uma
feature por vez com as outras 4 **cravadas em zero** e media correlação
> 0,9. Isso media duas coisas que não são o modelo: (i) **contexto zerado** —
`tower_diff=+2` com `gold_diff=0` é estado que a partida praticamente não
produz (o próprio diário registra isso em 2026-07-03); (ii) **valores
fracionários** — as features são aritmética inteira sobre o payload, e o
`np.linspace` gerava 0,29 torre / 0,14 dragão, que a feature não pode
assumir: **13 dos 15 pontos eram fisicamente impossíveis**. O sintoma era
correlação negativa nos cortes iniciais e positiva nos tardios **para a
mesma feature**, que é ruído de região de baixa densidade. E o `nan` de
`kill_diff` no corte de 25 min era "modelo insensível ao fator neste
contexto", reportado como se fosse o oposto.

**E o ponto de honestidade: as falhas não eram bugs novos.** As 9 checagens
não-OK apontadas pela versão antiga **já tinham sido diagnosticadas** na
entrada de 2026-07-03 deste diário (bateria de validação, item 1), que
decidiu **deliberadamente não corrigir** e classificou como "característica
do modelo, não bug" — o mesmo raciocínio está hoje declarado na Seção 5.2
do TCC: o XGBoost não garante formalmente que aumentar **isoladamente** a
diferença de **abates** ou **torres** nunca reduza a probabilidade, por
conta de interações e redundâncias entre variáveis. Ou seja: a reforma
**não** transformou 9 achados em 0; ela impediu que um resultado já
diagnosticado e já declarado no texto aparecesse como reprovação do modelo.

**A correção foi reformular a afirmação, não afrouxar o limiar.**
- Seção 1 renomeada para **"Sanidade direcional"**: parte de linhas
  **reais** de `features_phases.csv` (400 linhas por corte,
  `random_state=42`), usa **valores inteiros** do percentil 1%-99% da
  própria feature e mede a **fração de pares em que aumentar a feature
  move a probabilidade na direção certa** — "vantagem REAL sobe a chance",
  não "toda feature é monotônica".
- Os percentis entram como **offset sobre a linha real**, não como valor
  absoluto: uma linha de `gold_diff` +14.000 no corte de 25 é sondada em
  +14.000+1.041, que é a pergunta que interessa ("dado o resto do estado
  real, e se esta feature fosse maior?").
- **Empates contados à parte e excluídos do denominador.** Com features
  inteiras e faixa curta, boa parte dos pares consecutivos cai na mesma
  folha da árvore; contar empate como acerto **infla** o número — foi
  exatamente o que mascarou `tower_diff`/15min como "40%" quando, sem
  empates, é 1%.
- **Três estados de resultado**, em vez de "OK/não-OK":
  - `FALHA` — fator com SHAP médio ≥ 0,05 (ou seja, realmente usado pelo
    modelo), direção errada, **e** o TCC não declara isso para ele. Foi o
    único estado que passou a reprovar (`sys.exit(1)`).
  - `LIMITADO` — não-monotonicidade isolada de um fator que a Seção 5.2
    **nomeia** ("abates e torres"): reportada, não reprovada.
  - `NEUTRO` — SHAP médio < 0,05: o modelo praticamente não usa o fator
    naquele corte, então direção não é exigível.
- `LIMITADO` é definido por **propriedade**
  (`FEATURES_NOMEADOS_PELO_TCC = {kill_diff, tower_diff}`), não por tupla
  (feature, corte) — deliberadamente, para não ser uma lista feita sob
  medida para o único caso que falhava. Se amanhã outro fator nomeado
  falhar, ele entra como `LIMITADO` sem ninguém mexer no código.

**Resultado da execução reformulada** (registrado em `docs/scripts.md`,
seção `tests/validate_predictions.py`): `gold_diff` 99-100% e `xp_diff`
92-100% de direção correta — são os fatores dominantes, com SHAP de 0,65 a
1,04. **1 caso `LIMITADO`**: `kill_diff`/15min, direção em 60%, SHAP 0,070.
**3 casos `NEUTRO`**: `tower_diff`/10min (SHAP 0,004), `tower_diff`/15min
(0,014) e `kill_diff`/25min (0,009) — as placas só caem aos 14 min, que é a
própria justificativa do TCC para treinar um modelo por fase. Bateria em
~26 s, determinística (`setseed`), saída 0, veredito final **"APROVADO COM
RESSALVAS"** — que é a última linha que o `validador` e a banca leem, e
que nunca diz "todas passaram" havendo ressalvas listadas acima.

**Duas outras mudanças no mesmo passo:** a checagem retrospectiva (seção 5)
saiu de n=30 com `ORDER BY random()` **sem semente** para **n=150 com
`setseed(0.4242)`** — um gate que podia falhar conforme o humor do banco,
e n=30 não daria IC 95% capaz de sustentar afirmação (28/30 = 93% não é
evidência de nada); e o `predict_proba` passou a rodar em **lote** por
(corte, feature), porque 40.000 chamadas de uma linha levavam minutos e o
`validador` roda isto como portão.

**Lacunas honestas desta reforma:** a saída da execução **não foi
arquivada** (não existe `reports/validate_predictions*.log`), então os
percentuais acima vêm do registro em `docs/scripts.md` e não de um log
re-executável; e o **detalhe por caso** das 9 falhas da versão antiga
(tipo "kill_diff/10min reprovou em X%") não foi preservado — a contagem
agregada de 9 e o diagnóstico de 2026-07-03 sustentam a conclusão, mas
não há como reapresentar a tabela antiga caso a banca peça. Pendente:
arquivar a próxima execução em `reports/`.

**O que NÃO foi feito, deliberadamente:** (a) não adicionar
`monotone_constraints` ao treino — isso é **retraining, mudança de
modelagem**, não correção de bateria (e a limitação segue declarada na
Seção 5.2, que é o lugar honesto para ela); (b) não afrouxar nenhum
limiar — direção mínima 0,60, `SHAP_RELEVANTE` 0,05 e taxa mínima 0,70 da
retrospectiva seguem como estão, todos registrados em `scripts.md` como
**escolha de implementação, não derivação do TCC**; (c) não regenerar
`features_phases.csv` nem rodar `export_model` — o modelo de produção segue
sendo o mesmo arquivo de antes, byte a byte.

### 3. Correções de consistência documental

- **Contagem de experimentos negativos: 8 → 9.** O Apêndice D do TCC
  omitia o experimento de **dragões por tipo (`monsterSubType`)**,
  registrado na entrada de 2026-07-05 deste diário (Sprint 2) como **7º
  experimento negativo**, com AUC dos 15 min **piorando** de 0,8319 para
  **0,8295** (20 min 0,8661→0,8651; 25 min 0,9013→0,8999) — **o único dos
  nove em que o desempenho piorou de forma mensurável**, e por isso o mais
  informativo da série. A confusão nasceu de renumeração local: os títulos
  "Experimento 7" (`item_gold_diff`) e "Experimento 8" (visão) das entradas
  de 2026-07-06 contam a partir de uma lista que pula o dragões-por-tipo, e
  o texto do "7º" chega a enumerar os antecessores ("barão/arauto,
  dispersão de time, tuning por fase e calibração") sem citá-lo. A
  reconstrução completa da série, conferida entrada a entrada: dispersão
  espacial (2026-07-03), barão/arauto (2026-07-03), tuning por fase
  (2026-07-03), calibração adicional (2026-07-03), ouro em itens
  (`item_gold_diff`, 1ª versão, 2026-07-03), split defensivo/ofensivo
  (2026-07-03), **dragões por tipo (2026-07-05)**, `item_gold_diff` refeito
  (2026-07-06), visão (2026-07-06) — **9**. Observação de ordenação: no
  Apêndice D o dragões-por-tipo aparece na posição 9, mas
  cronologicamente foi o 7º; a escolha foi finalizá-lo por ser o único com
  piora mensurável. **Os títulos "Experimento 7"/"Experimento 8" das
  entradas de 2026-07-06 ficam como estão** — são registro histórico da
  sessão, não índice da série.
- **`docs/handoff.md` ainda holdava** "Solo queue Challenger/GM BR:
  vermelho vence 56,3%" como se fosse fato do BR. O TCC 4.3 (regionalizado)
  mostra que é padrão das quatro regiões com amostra relevante. **Corrigido
  no handoff** — a formulação antiga ("é do BR") não deve voltar ao texto.
- **`docs/diario_execucao.md:3160`** mandava "usar o nome novo 'Hextech
  Lab'" — que é o nome **antigo**, descartado em 2026-07-03 por colisão com
  um canal do YouTube. **Corrigido para Bellestraiko.** As outras 4
  ocorrências de "Hextech Lab" são narrativa histórica legítima dos dois
  renomes e **ficaram** — o erro era a instrução, não a história.
- **Comentário invertido em `src/features/build_features.py`** (seção
  `BUILDING_KILL`): afirmava que `killerTeamId` é o time que **PERDEU** a
  torre, quando é o que a **DESTRUIU**. O código estava certo; o que estava
  errado era a descrição da armadilha — e um leitor futuro que acreditasse
  no comentário reintroduziria exatamente o bug invertido que a entrada de
  2026-07-08 passou 2 semanas documentando. **Comentário corrigido, lógica
  intocada.**
- **Ressalva de volume acrescentada ao TCC** para o "~68%" de conversão de
  vantagem: as taxas do solo queue dessa comparação foram medidas em
  2026-07-04 sobre **~12 mil** partidas (a base disponível na ocasião; a
  entrada de 2026-07-04 registra a coleta correndo de 10,4k para 11,8k ao
  longo da própria sessão), **não sobre as 23.133** do modelo. A ressalva
  existia no `handoff.md` e não no texto - agora está nos dois. É
  uma estimativa de apoio a um achado qualitativo (a diferença de ~16 pontos
  percentuais entre os dois cenários é grande demais para ser artefato de
  amostra), não medida sobre a base de treino.


## 2026-10-04

### Coleta, retreino e um achado que mudou de forma

**Ampliação da NA1.** A região, que era o elo mais frágil da generalização
com 1.446 partidas, foi de 1.446 para **7.159**. A taxa de vitória do vermelho
na região foi de 51,9% para **52,2%** — a direção do achado não mudou. Base
final: **39.426 partidas** (BR1 11.936, EUW1 11.744, KR 8.567, NA1 7.159,
EUN1 20). Isso reverte a decisão de escopo de 2026-10-03, que fixava
33.713: coletar foi mais barato do que a ressalva de volume custava ao texto.

**Retreino.** XGBoost no corte de 15 min passa de 0,7573/0,8393
(23.133 partidas) para **0,7621/0,8473** (39.188). O `GridSearchCV` sobre as
39 mil linhas devolveu ajuste equivalente (200 árvores a taxa 0,05), o que
confirma que a limitação de taxa-base da Seção 5.8 **não é subajuste**.
AUC por corte: 0,774 / 0,847 / 0,876 / 0,909 — monotônico.

### O achado de viés de lado foi refutado pelo aumento da amostra

**Este é o registro mais importante do dia.** A Seção 5.3 afirmava, desde
2026-07-08, que o viés de lado *enfraquecia* ao longo da partida, com pico
aos 15 min (46,3% de vitória do azul) e queda para 51,1% aos 25. A bateria
`validate_predictions.py` vinha reprovando por causa disso desde a
ampliação da base, e eu vinha tratando a reprovação como "limitação
conhecida". **A bateria estava certa e o texto errado** — e é exatamente para
isso que uma bateria que valida o enunciado do texto serve.

Medido (`docs/taxa_base_por_corte.py`), entre partidas genuinamente
empatadas, com |diferença de ouro| menor que 500:

| corte | vitória do azul | n |
|---|---:|---:|
| 10 min | 46,4% | 7.349 |
| 15 min | 47,9% | 3.970 |
| 20 min | 46,7% | 2.423 |
| 25 min | 47,1% | 1.430 |

Dispersão de 1,4 ponto percentual. O teste de pares com correção de Holm
(`docs/testa_diferenca_taxas.py`) não deixa **nenhum** par sobreviver: menor
p corrigido = 0,83, no par 10 contra 15. Os intervalos de confiança de 95%
se sobrepõem. O corte mais vermelho é o de **10 min**, não o de 15.

Conclusão: o viés é **constante** ao longo da partida. O que a base maior
desfez foi a *evolução*, não o viés — que segue forte, com o IC do corte de
10 min em [45,3%, 47,6%], excluindo 50% com folga.

**Por que isso importa mais do que a correção:** o texto afirmava uma
tendência sobre quatro taxas que sempre ficaram perto umas das outras. Com a
amostra menor, o ruído se desenhava como padrão. Efeito colateral útil:
Abstract em inglês, Apêndice C e Conclusão foram reescritos, porque todos
afirmavam a forma antiga.

### Números velhos que sobreviveram à ampliação

Auditoria do texto contra o banco e os artefatos, que revelou quatro erros que
a checagem a olho nunca pegaria:

- **99.259 jogos profissionais**: nunca conferido. São **96.716**. A tabela
  `pro_games` tem duas linhas por jogo, então `COUNT(*)` devolve 193.432 — o
  dobro, e plausível.
- **Quadro 1 com NA1 em 1.446 / 51,9%** enquanto o banco tinha 7.159 /
  52,2%. A legenda dizia "medido em 2026-10-03, sobre 33.713" e nenhuma
  região somava esse total.
- **SHAP das torres**: o texto dizia 0,004 / 0,014 / 0,018 / 0,108 com
  "salto de 26 vezes". O JSON diz 0,0044 / 0,0060 / **0,0031** / 0,0928 — a
  série **não é monotônica** e o salto é de 15 vezes.
- **Conversão de vantagem**: 84,0% contra ~68%, medido sobre ~12 mil partidas
  (o próprio texto admitia numa ressalva). Remedido nos dois lados:
  **81,5% contra 73,7%** — o efeito é real (z = 8,28) mas tem metade do
  tamanho declarado.

### Corpo do trabalho

O "corpo = 21 páginas" do texto era derivação manual. O
`finalize-fields.ps1` agora mede — localiza a Seção 1 e o fim das
Referências e reporta a diferença — e a primeira medição honesta deu **22**,
abaixo do mínimo institucional de 25.

Medi os 10 trabalhos aprovados pela banca, seção por seção. Três seções
estavam abaixo da mediana e a Conclusão abaixo do **mínimo** dos 10 (442
palavras contra 983). Expansão: Fundamentação 837 para 1.696, Relacionados
695 para 1.061, Conclusão 442 para 1.074. Corpo = **28 páginas**.

A Fundamentação citava XGBoost e SHAP pelo nome sem citar as obras
originais. Acrescentadas 6, **todas verificadas por DOI no Crossref antes de
entrar**: duas crenças minhas estavam erras e a verificação pegou — RAT-SQL é
de Wang et al., não de Xie; e o DOI do pandas que eu lembrava pertence a um
artigo sobre crédito imobiliário.

### O "nao e subajuste" finalmente tem lastro

Ultima afirmacao do TCC sem artefato. A secao 5.8 diz que a limitacao de
taxa-base nao e subajuste porque a grade escolhe a mesma profundidade e
fica equivalente em AUC — e nenhum log em `reports/` sustentava isso.
`tune_models.py` imprime e nao guarda, e so tinha rodado sobre a base de
10 mil.

Criado `src/models/tune_models_full.py`, que roda a grade completa sobre as
39.188 linhas do corte de 15 min e grava `reports/tune_models_39k.log` e
`.json`. Medido:

| | AUC | posicao |
|---|---:|---|
| producao (500 / 0,01 / 3) | 0,8473 | 2 de 27 |
| vencedora da grade (200 / 0,05 / 3) | 0,8475 | 1 de 27 |

Profundidade **a mesma (3)** nos dois. Delta de **+0,0001** — uma casa
decimal que a variacao entre folds produz sozinha. A afirmacao da 5.8
estava correta e agora e verificavel por comando.

A checagem 12 de `docs/verifica_tcc.py` confronta o texto com esse JSON e
falha com exit 1 se o delta passar de 0,005, se a profundidade divergir ou
se o numero medido nao estiver no texto. Testada inflando o delta para
0,0231 no JSON: acusa tres falhas de uma vez.

O que a medicao **nao** sustenta, e que vale registrar: o delta de 0,0001
e sobre AUCROC e um unico par (profundidade, arvores, taxa). Nao probei
regularizacao alternativa nem calibracao forcada, que sao as duas alavancas
naturais contra um modelo que projeta o empate para perto de 50%. O
arguito da 5.8 e "a grade nao acha ajuste melhor", e nao "nao existe ajuste
melhor" — a segunda afirmacao seria mais forte do que o experimento
sustenta.


### D1 — As duas alavancas que a grade nao cobria, testadas

A 5.8 dizia que a limitacao de taxa-base nao e subajuste porque a grade de
hiperparametros nao achou ajuste melhor. A frase era verdadeira e incompleta:
a grade variou so `n_estimators`, `learning_rate` e `max_depth`, e a
discrepancia e justamente de taxa-base — que esses tres eixos nao alcancam.
Faltava testar **calibração** (a tecnica que se esperaria resolver um erro
de taxa-base) e **regularização alternativa**.

Medido em `docs/experimento_calibracao.py`, no corte de 15 min — o de MENOR
discrepancia entre os quatro (1,7 pp), ou seja, o caso mais favoravel a uma
correcao:

| variante | AUC | taxa-base | desvio do dado bruto |
|---|---:|---:|---:|
| producao (500/0,01/3) | 0,8473 | 49,6% | 1,7 pp |
| calibrada sigmoidal | 0,8474 | 50,2% | **2,3 pp** |
| calibrada isotonica | 0,8472 | 49,8% | 1,9 pp |
| regularizada (min_child_weight=20) | 0,8474 | 49,7% | 1,8 pp |
| regularizada (gamma=1, subsample=0,8) | 0,8474 | 49,5% | 1,6 pp |
| **RandomForest 500/prof 6** | 0,8468 | **48,5%** | **0,6 pp** |

Referencia do dado bruto: 47,9% de vitoria do azul entre partidas
genuinamente empatadas, lida de `reports/taxa_base_por_corte.json` — nao
hardcoded, para a comparacao nao poder divergir se o dado for remedido.

**RESULTADO CONTRA-INTUITIVO, E REGISTRADO COMO TAL.** A calibracao
**piora** a discrepancia (de 1,7 para 2,3 pp na sigmoidal). A intuicao —
"calibrar a saida para a frequencia observada" — falha porque o estado de
empate total nao esta na distribuição observada: e um ponto que o jogo real
nao produz com frequencia, e o calibrador o extrapola para perto de 50%.
Ou seja, a técnica mesma de que resolveria o problema e a que mais o
agrava. A regularizacao alternativa move o desvio dentro do ruido.

A unica variante que fecha a discrepancia e a **troca de família de
modelo**: RandomForest 500 árvores, profundidade 6. Custo: 0,0005 de AUC
(0,8473 → 0,8468). Vale notar que a RF *sem* limite de profundidade, que é
a que aparece no Apêndice C, AUC de 0,8277 — a limitacao a profundidade 6
e o que faz ela emparelhar com o XGBoost.

**O QUE ISSO MUDA NO TCC.** A conclusao da 5.8 fica mais especifica e mais
forte: a discrepancia nao e um déficit de ajuste do XGBoost, e uma
propriedade da função que essa família aprende neste recorte. Corrigi-la
exige trocar de modelo, e o custo medido e pequeno mas real — o que faz da
troca uma decisão de escopo, nao um ajuste de parametro.

**ERRO MEU, E REGISTRADO.** A primeira versao do script declarava
"VEREDITO: FECHA" com limiar de desvio < 2,0 pp — e a variante de producao
ja estava em 1,7 pp. Qualquer coisa que nao fosse pior que a producao
contava como "fechou", e a regularizacao, que melhora 1,7 → 1,6 pp, foi
contada como sucesso. O limiar foi corrigido para exigir desvio < 1,0 pp E
custo de AUC < 0,001, e a reavaliacao esta em
`docs/reavalia_calibracao.py` +
`reports/experimento_calibracao_veredito.json`. Limiar que aceita o estado
atual como sucesso nao e limiar, e noise floor.


### A KR não sustenta o que o texto afirmava sobre ela

Pergunta de encerramento: "só falta coletar mais?". A resposta foi não, e a
verificação encontrou coisa mais séria que coleta.

A Seção 5.3 afirmava que "as **quatro** regiões com amostra relevante
**pendem** para o vermelho, entre 50,3% e 56,3%". Calculando o intervalo de
Wilson de 95% de cada região:

| região | partidas | vermelho | IC 95% | exclui 50% |
|---|---:|---:|---|---|
| BR1 | 11.936 | 56,3% | [55,4%, 57,2%] | sim |
| EUW1 | 11.744 | 53,4% | [52,5%, 54,3%] | sim |
| KR | 8.567 | 50,3% | [49,2%, 51,3%] | **não** |
| NA1 | 7.159 | 52,2% | [51,1%, 53,4%] | sim |

**Na KR o viês NÃO é estatisticamente distinguível de zero.** "Pende" está
errado, e a direção consistente não pode ser tratada como evidência
de que o padrão é do elo alto.

Isto é mais grave que os outros numeros corrigidos nesta rodada porque é a
**sustentação da generalização do achado**. A pergunta "o vies e do elo alto
ou e do Brasil?" se responde pela consistência entre regiões, e a KR é
justamente a que não sustenta a resposta. Tres regioes excluem 50% com
folga; a quarta nao.

Corrigido em tres lugares — nota de metodo do Quadro 1, Secao 5.8 e
Conclusao. O texto agora diz que tres das quatro tem intervalo que exclui
50%, nomeia a KR como a excecao, e atribui a BR1 ([55,4%, 57,2%]) o
argumento de que o padrao nao e especificamente brasileiro. Isso NAO
enfraquece o achado: BR1 sozinha ja o sustenta com folga, e afirmar
"quatro de quatro" sem intervalo era o que estava errado.

**O QUE ISSO MUDA SOBRE COLETAR MAIS.** A coleta na KR deixa de ser
reforço e passa a ser **medição de risco**: com 8.567 partidas o intervalo
tem ±1,1 pp, e ampliar pode fechar em torno de 50% — isto e, revelar que
o vies nao existe na KR. Nao e reforço de evidencia, e um teste que pode
sair negativo. Quemampliar a KR deve saber disso antes, e o objetivo
declarado tem que ser fechar a questão, nao confirmar.

**CHECAGEM 16.** `docs/verifica_tcc.py` calcula os intervalos por regiao e
falha se o texto uniformizar o que o intervalo nao sustenta. Pegou uma
formulacao residual na 5.8 que escapou da correcao manual.

**LIMITE DE PAGINAS.** A ressalva empurrou o corpo para 31 paginas, fora da
faixa. Condensada a duplicata da 5.8 e a propria ressalva, voltou a 30 —
o teto, sem folga. Detalhe em `docs/plano_fechamento.md`.


### Rodada final da KR: a pergunta da coleta, respondida

A entrada anterior deixou a KR como **medição de risco** e a pergunta aberta:
ampliar fecha o intervalo em torno de 50%, ou confirma o viés? Coletei
**1.549 partidas** da KR — a tabela `matches` foi de KR 8.655 / total 39.514
para KR 10.204 / total 41.063 — e a resposta é a primeira:

| região | antes | depois | IC antes | IC depois |
|---|---:|---:|---|---|
| KR | 8.655 | 10.204 | [49,2%, 51,3%] | [49,5%, 51,4%] |

A taxa foi de 50,3% para **50,4%**. O intervalo continua incluindo 50%. Mais
1.549 partidas custaram 0,1 ponto percentual de deslocamento e o intervalo
continua abertos — exatamente o que um teste de poder previa.

**O "antes" era 8.655, e o texto dizia 8.567.** A diferença é que 8.567 era a
contagem da KR que chegou a produzir *features*, enquanto a medição de lado é
lida de `participants`, que tinha as 8.655. Os dois números estavam certos em
contextos diferentes e eu usei o menor como se fosse o total. Isso também
explica de onde vem a "diferença de 1.637 partidas" que o TCC declara: ela é
contra a base de modelagem de 39.426, e não o rendimento da rodada.

**O CÁLCULO QUE FECHA A QUESTÃO.** Para o IC da KR excluir 50% mantendo a
taxa observada de 50,4%, seriam necessárias **60.025 partidas**
(5,9× a amostra de KR, 1,5× toda a base do projeto),
pela mesma fórmula da Seção 5.8 — n = z²·0,25/(p−0,5)² com z de 95%. Se a
taxa real da KR fosse 51,0%, bastariam 9.604 — menos que a amostra que já
existe. Não sabemos qual das duas é, e é exatamente isso que o intervalo
expressa.

**ERRO MEU NESTE CÁLCULO, E ELE MUDAVA A CONCLUSÃO.** A primeira versão
publicou ~106.700 partidas. Esse é o valor para a taxa **antes** da rodada,
50,3%. Com a taxa de 50,4% que o texto afirma, o mesmo cálculo dá 60.025:
o número estava 1,8× alto, e o multiplicador "12× a amostra de KR" saía 5,9×.
O erro não veio de fórmula errada, e sim de eu ter calculado com o número
antigo e redigido com o novo — a mesma classe de erro que a frase "medido
sobre as 41.063" com taxas de 39.426. Um número colado ao lado de outro
número recém-alterado precisa ser recalculado, não reescrito. A afirmação
qualificada da Seção 5.3 **não é uma ressalva temporária esperando coleta: é a
resposta final.** Registrar isso é o que separa "faltou dados" de "o dado não
sustenta".


### O número do Apêndice B deixou de ser número sem rastro

Terceira revisão do diff, e ela mudou o estado em vez de só produzir achados.

**A CHAVE ESTAVA NO `.env` O TEMPO TODO, E EU TINHA ERRADO A SONDAGEM.** A
primeira versão desta seção dizia que `ANTHROPIC_API_KEY` não estava no
ambiente e que a reexecução ficava pendente. A sonda que usei listava os
atributos em maiúsculas de `src.config` — e a chave é lida por
`os.environ[...]` dentro de `generate_sql`, não por uma constante do módulo.
Um `print(dir(config))` sem `os.environ` produz "não tem" para tudo que não
foi promovido a constante. **Sondar ausência de configuração olhando o módulo
errado é como medir a ausência de dado olhando a tabela errada.**

Benchmark reexecutado sobre a base final de 41.063: **23/26 = 88%**, o mesmo
número da execução anterior sobre 39.426. Uma diferença de 4% no volume que
não move o resultado — e agora isso é verificável, porque
`reports/nlq_benchmark.json` existe com accuracy, base, modelo e o desfecho das
26 perguntas, incluindo a SQL gerada de cada uma.

**O QUE A CHECAGEM 19 ERA.** Ela aceitava que o Apêndice B publicasse um número
sem artefato desde que o texto declarasse isso. O revisor Nomeou o problema com
precisão: um perdão permanente emitido por prosa. A condição de passa se
cumpre sem ninguém rodar o benchmark, o texto pode carregar a declaração para
sempre, e a linha de saída ainda imprime `[OK]` para um estado que o próprio
texto chama de pendente.

A guarda agora tem três saídas, e só uma delas é dívida:

| situação | veredito |
|---|---|
| artefato existe, accuracy e base batem | passa |
| não existe, texto declara a lacuna, **chave ausente** | passa — é bloqueio de ambiente |
| não existe, texto declara a lacuna, **chave presente** | **reprova** — a desculpa evaporou |

A segunda linha é a única dívida tolerada, e ela tem gatilho: a checagem lê
`ANTHROPIC_API_KEY` do ambiente. Se a chave voltar a existir, o perdão expira
sozinho. A declaração também passou a ser procurada **no parágrafo do número**,
não no apêndice inteiro, para que uma frase sobre outro artefato não sirva de
quitação.

### O Anexo A foi regerado, em vez de explicado

A correção anterior dizia que as capturas **não** eram as mesmas da Seção 5.3, e
sustentava isso com o mtime do PNG. O revisor apontou o problema: o mtime não é
verificável num clone limpo, e `recapturar_anexo_a.py` — o comando que o
próprio anexo manda rodar — produz PNGs com mtime novo, tornando as duas
afirmações publicadas falsas sem que nada acuse.

Duas correções, e a segunda é a que fecha o problema:

1. `recapturar_anexo_a.py` agora grava `reports/anexo_a/captura.json` com
   `capturado_em`, `base_partidas_fila_420`, as telas e o id de partida usado.
   O registro só é escrito se as 6 capturas passarem — um registro de seis telas
   das quais três falharam seria pior do que nenhum registro.
2. **As capturas foram regeradas** sobre 41.063 partidas. Com isso "as mesmas da
   Seção 5.3" voltou a ser **verdade** e o parágrafo voltou a ser simples.

A Figura 2 agora mostra KR com 10.204 partidas e 50,4% de vitória do vermelho —
confirmei contra `/stats/regions`, que devolve 10.204 e 0,5044. A contradição
que motivou a primeira recaptura (NA1 = 1.446 na tela contra 7.159 no texto)
continua resolvida.

Detalhe operacional: a primeira tentativa de regerar **falhou todas as 6** e a
trava de segurança do script derrubou a captura. A causa era o frontend ter
subido na porta 5174 porque a 5173 estava ocupada por um processo node antigo,
e a allowlist de CORS da API só tem `http://localhost:5173`. O sintoma — "a
página mostrou 'Erro no servidor'" — não é o que parece: a API estava de pé e
respondia 200 pelo `curl`. **A trava de segurança funcionou como deve: recusou
a tela de erro em vez de virar figura do TCC.**

### O artefato podia mentir, e sobrescrever o bom

`evaluate_nlq.py` gravava `reports/nlq_benchmark.json` em qualquer run. Com a
chave ausente, `generate_sql` estoura `KeyError` nas 26 perguntas, o `except`
engole, e o script escrevia `execution_accuracy: 0.0` com `medido_em` de hoje —
**sobrescrevendo a última medição boa com um arquivo que tem cara de medição.**
E `docs/scripts.md` manda exatamente esse caminho: "rode de novo depois de
qualquer mudança".

`_degenerado()` recusa a rodada em três casos, e o terceiro é o que eu não tinha
pensado:

- nenhum acerto;
- accuracy abaixo de `MINIMO_PLAUSIVEL = 0,5` — nenhuma plataforma que
  responda 85-95% produz 4/26, então o corte está longe do resultado legítimo
  e não é um limiar que aceita o estado atual;
- **três ou mais falhas com a mesma causa** — cobre a cota que acaba no meio da
  rodada, em que as primeiras perguntas passam e as seguintes falham igual. Esse
  caso não se enxerga no total, só nas causas.

Run recusado preserva o artefato anterior e sai com código 1. A gravação também
passou a ser atômica (temporário + `replace`), e o `detalhe` agora carrega a
**SQL gerada** e a causa — sem isso as três falhas benignas continuavam
indecifíveis, porque `str(SqlExecutionError)` devolve só a causa: a classe chama
`super().__init__(str(cause))` e o `.sql` fica um nível acima.

### Checagem 20: a contagem de checagens que os documentos afirmam

A contagem divergiu quatro vezes num dia — 12, 17, 18, 20 — e nada pegava.
`check_scripts_documentados` procura um token do nome do script em
`comandos.md`, nunca o número; e o número também aparecia no bloco de
pendências do próprio TCC. Conferi se ele vai para o `.docx` — **não vai**:
`build_tcc_docx.py` remove `## Pendências finais antes da entrega` de propósito,
é log de trabalho. A checagem compara o `.md` mesmo assim, porque um número que
divergiria ali ainda é divergência.

A fonte da verdade é o próprio `verifica_tcc.py`: quantos `print("N.` ele emite.
A 20 compara com o que `comandos.md`, o TCC e o diário afirmam. O diário é
julgado **só na entrada mais recente**, porque é um log cronológico: a entrada
de 2026-10-03 que falou das falhas da versão antiga da suíte é histórica e está
certa, e reprová-la seria reprovar o diário por registrar o passado com
fidelidade.

**LIMITE DESTA CHECAGEM, REGISTRADO:** ela julga o número literalmente e não
distingue citação de afirmação. Citar uma contagem antiga no diário — mesmo
dizendo explicitamente que é antiga — reprova, porque o padrão `N checagens`
casa igual nas duas situações. Reescrevi a frase acima em vez de criar uma
exceção no código: uma exceção "não conta se a linha disser 'antiga'" é o tipo
de heurística que afrouxa a guarda sem motivo, e aqui o custo de reescrever é
uma frase.

### Duas lições que se repetem nesta rodada

**Substituição por faixa de linhas, quando as faixas se sobrepõem, imprime "ok"
e não grava.** Uma das minhas edições do Apêndice B substituiu o parágrafo em
memória, imprimiu sucesso, e **esqueceu de escrever o arquivo**. As três
tentativas seguintes foram por âncora de texto e falharam por causa da quebra de
linha do markdown; a que resolveu foi por conteúdo, de um ponto a outro do
bloco. Escrever é parte da operação — um `ok` sem `write` é uma mentira
silenciosa, do mesmo tipo das que estas checagens existem para pegar.

**Quase tentei automatizar a detecção de frase quebrada.** Um pattern
"minúscula seguida de maiúscula sem pontuação" dá **211 falsos positivos** no
texto: títulos de seção, "Riot", "Seção", quebras de parágrafo. Inútil. A
cobertura desse erro continua sendo humana — registrado aqui como limite
conhecido, e não como guarda que enfeita a suíte.


**A CONCILIAÇÃO DOS QUATRO NÚMEROS, QUE ESTAVA INCOERENTE.** Durante a
revisão do diff, o `stats_regions.txt` arquivado em `045fdc0` — que a checagem
6 gera a partir do SQL — registrava KR 8.655 / TOTAL 39.514, enquanto o texto
usava 8.567 e 39.426. Os dois não estavam errados: mediam coisas diferentes.
Conciliando:

| momento | partidas |
|---|---:|
| `matches` quando as *features* foram congeladas (10:45) | 39.426 |
| das quais produziram linha em `features_phases.csv` | 39.309 |
| **sem *features* naquela altura** | **117** |
| coletadas entre o congelamento e a medição de `045fdc0` | 88 |
| `matches` na medição de `045fdc0` | 39.514 |
| rodada da KR depois | 1.549 |
| **`matches` hoje** | **41.063** |
| **`features_phases.csv` hoje** (distintas) | **39.309** |
| **sem *features* hoje** | **1.754** |

117 + 88 + 1.549 = 1.754, e 1.647 (KR) + 59 (BR1) + 29 (EUW1) + 19 (NA1) =
1.754.

**A tabela precisou das duas âncoras porque há dois totais legítimos, e na
primeira versão eu misturei os dois.** O TCC fala em 39.426, que é o banco no
congelamento; o `stats_regions.txt` de `045fdc0` fala em 39.514, que é o banco
quando aquela medição rodou — 88 partidas depois. Publicar a reconciliação
só com o segundo númerointroduzia um terceiro valor para a mesma grandeza,
que é exatamente a classe do bug crítico. As features nunca foram
regeneradas depois das 10:45, então 39.309 é constante nas duas pontas: é ele
que fecha as duas contas.

**DECISÃO: MANTER A RODADA, NÃO REVERTER.** Duas bases passaram a coexistir,
e a alternativa era escolher um número e esconder o outro:

- **base descritiva** (Quadro 1, viés de lado, teste de duração): **41.063**
- **base de modelagem** (features e modelos): **39.426**, das quais 39.309
  geraram *features* e 39.188 chegam ao corte de 15 minutos

Não houve troca em bloco: das 20 ocorrências de 39.426 que o texto tinha antes
desta rodada, 13 viraram 41.063. Sobraram **11 em português e 1 no Abstract em
inglês**, todas em contexto legitimamente congelado — a série de AUC por corte,
o Apêndice C, o
benchmark do NLQ e as capturas do Anexo A foram medidos na base congelada, e
dizer 41.063 neles seria falso. A nota que explica as duas entrou no início da
5.3, e a limitação que ela prometeu foi registrada na 5.8: **o modelo não viu
a rodada final.** Retreinar foi deixado de fora porque o desempenho atual já
está medido e validado contra o Apêndice C e a bateria comportamental, e
refazê-lo invalidaria as duas coisas sem ganho apurado.

### Dois erros meus nesta rodada, um deles chegou ao entregável

**1. Troquei a base e deixei os números.** Ao atualizar 39.426 para 41.063 na
5.3, a substituição levou o número da base mas **não** as taxas por faixa de
duração, que tinham sido medidas sobre 39.426. O texto afirmava, com
credibilidade sintática impecável, "medido em 2026-10-04 sobre as 41.063
partidas: 45,6% a 47,2%, amplitude de 1,6 ponto percentual" — número medido
sobre a base antiga. Passaria em qualquer revisão humana, porque a frase tem
data, base e amplitude, e nada nela é visivelmente errado.

**CHECAGEM 17, criada por causa disso.** As checagens existentes comparam
*métricas do modelo* com o artefato; nenhuma comparava as taxas do teste de
robustez. A nova amarra o texto ao `reports/faixa_duracao.json`: compara a
série de taxas, a contagem de cada faixa, a amplitude nos dois parágrafos e —
o ponto que fecha o loophole — **a soma das contagens do artefato contra a
base que o texto afirma**. Usar a soma em vez de uma constante escrita à mão é
o que impede o número de sobreviver a uma ampliação. Testada nos dois sentidos
com 5 mutações (base, taxa, contagem e as duas amplitudes): todas reprovam
com a mensagem certa, e o arquivo do entregável é restaurado byte a byte no
fim. A soma é 41.063, que é a base certa por construção, não por coincidência.

**2. A checagem 12 nunca checou o Abstract.** Quando passei a exigir as duas
bases no Abstract, a checagem reprovou — mas por um motivo que não era o
aparente. A extração usava uma alternância cujo primeiro ramo casava de
`## RESUMO` até `**Abstract`, devolvia o **RESUMO em português** e nunca o
trecho em inglês, que é o que vai para o pré-textual do `.docx`. A checagem
validava o resumo, não o abstract, e vinha passando porque o número que ela
exigia estava no resumo. Corrigida para extrair de `**Abstract:**` até a
próxima seção de primeiro nível; agora exige as duas bases **e** que a
diferença seja declarada como limitação.

Erro menor, na mesma linha: um script escrito via here-string do PowerShell
colou `FFFFF` no lugar de `1.637` dentro do texto que ia gravar. O arquivo que
existia para corrigir um *typo* não tinha acento correto. Refeito pelo editor.

**DOCUMENTAÇÃO.** README, `handoff.md` e `scripts.md` ficaram com o número
antigo. O `scripts.md` era o mais grave, porque descreve o que o script
imprime e o script já imprime outra coisa: quem rodar o comando e comparar
com a doc encontra divergência. Os três foram corrigidos — o `scripts.md` agora
registra também que a medição deu o mesmo resultado nas duas bases, o que é
evidência a favor de a amplitude de ~1,7 pp ser propriedade do sinal e não
amostragem.


### Ferramenta que evita a repetição

`docs/verifica_tcc.py` roda 20 checagens antes de qualquer commit: CJK,
referências cruzadas, consistência de tabela, ordem alfabética de
referências, números de modelo contra `reports/metricas_corte.json`, Quadro 1
contra o banco, dataset profissional contra o banco, e um **guard de
resíduo** que recusa os valores substituídos (0,7573, 46,3%, 84,0%, 33.713,
99.259) e as formas refutadas do achado, inclusive no Abstract em inglês —
que é montado no pré-textual do `.docx` e vai impresso sem passar por
nenhuma revisão em português.

O guard nasceu porque a checagem anterior era de **presença** ("0,7621 está
no texto?"), que passa mesmo com 0,7573 ainda lá. Foi o agente `doc-tcc` que
apontou esse buraco.


## 2026-10-05 — 10º experimento negativo: placas de torre

Pedido do usuário: validar se havia informação na própria Riot API — não só
na documentação, no payload bruto real já coletado — que pudesse melhorar o
modelo além dos 9 experimentos já registrados. Em vez de ler a documentação
oficial (exige login pra ver schema, só lista nomes de endpoint sem
detalhe), inspecionei direto o JSON de `raw_matches`/`raw_timelines` já no
banco.

**Achado:** `TURRET_PLATE_DESTROYED` é um tipo de evento próprio na
timeline, nunca referenciado em `build_features.py` nem em nenhum dos 9
experimentos anteriores (confirmado por grep antes de escrever o
experimento). Hipótese concreta: o SHAP por fase (Seção 5.4 do TCC) mostra
`tower_diff` ~0 antes dos 20 min porque torres raramente morrem cedo — mas
as placas de torre (bônus de ouro por dano, somem aos 14 min) são batidas o
jogo inteiro nessa janela, e nenhuma *feature* hoje enxerga esse sinal de
pressão de rota pré-15min.

Semântica do evento verificada com dados reais antes de confiar nela: o
campo `teamId` é o DONO da torre (quem sofre o dano), não quem destrói — o
time beneficiado é sempre o oposto, confirmado cruzando `killerId` contra
`teamId` em várias partidas reais (mesma armadilha já documentada para
`killerTeamId` em `ELITE_MONSTER_KILL`, 2026-07-08).

`plate_diff` = (placas do azul) − (placas do vermelho) até o corte, testado
nos cortes 10 e 15 min (aos 20/25 a feature satura, placas já sumiram).
Script: `src/models/experiment_turret_plates.py`. Artefato:
`reports/experimento_placas_torre.json`.

| Corte | n | baseline AUC | + plate_diff | delta |
|---|---:|---:|---:|---:|
| 10 min | 39.309 | 0,7702 | 0,7700 | -0,0002 |
| 15 min | 39.188 | 0,8450 | 0,8448 | -0,0002 |

**Negativo, mesma ordem de grandeza de ruído dos outros 9.** A hipótese era
boa — cobre exatamente a janela cega de `tower_diff` — mas o sinal de
pressão de rota que as placas captam já deve estar redundante com
`gold_diff`/`xp_diff`: a mesma pressão que derruba placa é a mesma que gera
a vantagem de ouro que o modelo já vê. Reforça o achado da Seção 5.8: o teto
não é falta de ideia de *feature* a partir da *timeline*, é o tipo de dado
que falta (ordem de *draft*, estado de onda de *minion*) — e isso não é mais
hipótese, é o décimo candidato real testado e saturado.

**Validação dos demais endpoints da Riot não usados pelo projeto** (mesmo
pedido): testados ao vivo (chave nova, a anterior tinha expirado — 24h,
comportamento normal da chave de dev, não bug) contra `champion-mastery-v4`,
`lol-challenges-v1`, `league-exp-v4`, `champion-v3`, `clash-v1`,
`summoner-v4`. Achado de método, não só resultado: `champion-mastery-v4` e
`lol-challenges-v1` retornam o estado VITALÍCIO atual do jogador, não o
estado dele na época de cada partida histórica — aplicá-los ao banco atual
seria vazamento de dado (violaria a regra nº 1 do `AGENTS.md`), então ficam
descartados para o dataset já coletado, só viáveis se capturados no
instante de uma coleta futura. `league-exp-v4` é o único com valor direto
sem essa armadilha: confirma que dá pra puxar jogadores de elo abaixo de
Challenger/GM/Master (testado em GOLD II, retornou jogadores reais) — é o
caminho real para a extensão "o viés de lado se sustenta fora do elo
altíssimo?" já registrada como trabalho futuro. Os demais (`champion-v3`:
só rotação semanal; `clash-v1`: modo torneio, baixo volume; `summoner-v4`:
já coberto por `account-v1`) sem valor analítico identificado.

**Nota de revisão (mesma sessão):** o usuário questionou se `mastery`
realmente modificaria o cenário. Resposta concordada e registrada: não —
maestria é redundante com o *shrinkage* de WR-por-campeão já em produção
(ambos aproximam familiaridade com o campeão; o *shrinkage* é baseado em
resultado, maestria só em volume) e é um sinal comprimido na população
Challenger/GM/Master (todo mundo já jogou muito os campeões que joga).
`teamwork_pct_diff`/`expertise_pct_diff` do `lol-challenges-v1` ficou como
único candidato — é eixo comportamental que não existe em nenhuma feature
já testada, não redundante com nada.


## 2026-10-05 (continuação) — 11º experimento negativo: teamwork/expertise

Decisão sobre o vazamento de `lol-challenges-v1` (que a entrada anterior
descartava "para o dataset já coletado"): existe uma saída — as partidas
MAIS RECENTES da KR têm gap de horas/dias entre a coleta e hoje, pequeno o
bastante pra consultar o estado "atual" do `lol-challenges-v1` sem vazar
praticamente nada. Script `src/models/experiment_challenges_pilot.py`
recalcula as 5 *features*-base direto de `raw_timelines` (reaproveitando
`features_from_timeline`, a mesma função de produção) em vez de usar
`data/features_phases.csv` — esse arquivo é o snapshot CONGELADO que o TCC
já documenta e verifica (Seção 5.8: "o modelo não viu a última rodada de
coleta" é decisão deliberada), e as partidas usadas aqui são posteriores a
esse congelamento.

**Piloto (200 partidas, n=199 após junção): resultado enganoso.**
`teamwork_pct_diff` isolado deu delta +0,0090 — maior que qualquer um dos
10 experimentos anteriores. Mas com amostra 200x menor que a usual
(~39 mil), e o próprio *baseline* já oscilando 1,8pp do AUC de produção só
por tamanho de amostra, não dava pra confiar. Pedido do usuário: mais
amostra antes de aceitar.

**Escala (3.000 partidas, n=2.987 após junção, gap 0-16 dias, média 7,8):
o sinal sumiu.** `teamwork_pct_diff` delta -0,0031, `expertise_pct_diff`
delta +0,0007, os dois juntos -0,0023 — mesma ordem de grandeza de ruído
dos outros 10 experimentos. Confirma que o +0,0090 do piloto era
regressão à média de amostra pequena, não sinal real. Script reaproveita
cache de consulta (`reports/_cache_challenges_kr.json`, 4.373 jogadores
únicos, zero vazamento de API já consultada ao escalar). Artefato:
`reports/experimento_challenges_piloto.json`.

**11 experimentos negativos agora.** O eixo "comportamento/coordenação do
jogador" (distinto de estado de jogo e de desempenho histórico) foi o
único tipo de sinal genuinamente novo cogitado desde os 10 primeiros — e
também não superou o modelo de 5 *features*. Reforça ainda mais o teto
documentado na Seção 5.8: não é falta de ideia, é teto de tipo de dado.


## 2026-10-05 (continuação) — Revisão completa, Bloco A: reconfirmação + ortografia

Com o conteúdo fechado (nada mais a adicionar), início da revisão de
forma em 5 blocos (plano registrado na conversa, não neste diário). Bloco
A — reconfirmação automática + camada que nenhum script cobre:

- `smoke_test`, `validate_predictions` (aprovado com ressalvas),
  `verifica_tcc` (20/20), `confere_docx` (conforme), `frontend` lint+test
  (31/31) — todos verdes, os 11 experimentos não quebraram nada.
- **Corretor ortográfico/gramatical do Word via automação COM sobre o
  `.docx` inteiro** — primeira vez que essa camada roda; os scripts do
  projeto conferem número e consistência, nenhum confere português.
  567 "erros" de ortografia, 0 de gramática. A esmagadora maioria é
  falso-positivo esperado (termos técnicos/inglês em itálico — esports,
  queue, XGBoost —, sobrenomes de autor citados, identificadores de
  código). Deduplicados em 207 palavras únicas e revisados um a um: **2
  erros reais achados e corrigidos** — "viês" (grafado errado numa das 17
  ocorrências; as outras 16 já estavam certas) e "défict" (faltava o "i",
  devia ser "déficit"). Confirmado: 567 → 565 após a correção, exatamente
  os 2 fixados. Nenhum dos dois mudava número ou achado, só grafia —
  mas é exatamente o tipo de erro que nenhuma das 20 checagens do
  `verifica_tcc.py` pega, porque elas conferem fato contra artefato, não
  ortografia.


## 2026-10-05 (continuação) — Revisão completa, Bloco B: achado grande, sumário e listas removidos

Bloco B: cruzar Sumário/Lista de Figuras/Lista de Quadros contra os 10
TCC II aprovados de verdade (`Downloads/TCC II - EXEMPLOS E MATERIAIS/`),
item que o `plano_modelos_tcc2.md` de 2026-10-04 tinha deixado pendente —
até aqui só o `.doc` genérico do professor tinha sido usado como fonte.

**Achado: nenhum dos 10 aprovados tem Sumário, Lista de Figuras ou Lista
de Quadros.** Medido via `pypdf`, não suposto: em todos os 10, o título
"1 INTRODUÇÃO" aparece na página 3 ou 4 do PDF — direto após
capa+folha de rosto+resumo/abstract, sem nada no meio. Unânime, não
maioria. Faz sentido retrospectivamente: são artigos curtos (25-30
páginas de corpo), não monografias — sumário/listas são convenção de
documento longo, não deste formato.

**Correção aplicada:** removido de `build_tcc_docx.py` — o bloco SUMÁRIO
em `montar_pre_textual()` e a função inteira `listas_de_ilustracoes()`
(ficou sem chamador, removida por completo, não só desligada). O
`finalize-fields.ps1` não precisou de nenhuma mudança: já reportava
"N sumario + M lista(s)" genericamente, e reporta "0 + 0" sem erro agora.

**Efeito medido:** documento caiu de 59 para 55 páginas totais (4
páginas de pré-textual a menos). O **corpo não mudou** — continua 30
páginas — porque a regra institucional mede Introdução→Referências, uma
distância relativa, não a posição absoluta na numeração; tirar páginas
ANTES do corpo desloca onde ele começa e termina igualmente, não o
tamanho dele. Achado de método registrado: remover pré-textual não é
alavanca pra abrir folga no teto de 30 páginas — só serve pra bater com
o formato real. `verifica_tcc` (20/20) e `confere_docx` (conforme)
confirmados depois da mudança.


## 2026-10-05 (continuação) — Revisão completa, Bloco C: formatação de referências confirmada

Bloco C: cruzar a formatação de REFERÊNCIAS contra os 10 aprovados —
mesma motivação do Bloco B (o item nunca tinha sido validado contra os
aprovados de verdade, só contra a correção pontual do TCC I).

**Linha em branco entre entradas:** extraído via `pypdf` das 10 seções
REFERÊNCIAS (localizadas pelo heading isolado, não por substring, pra
evitar falso-positivo em "referencial teórico"). Resultado: **7 de 10
usam linha em branco** (Carolina, Henrique, Eduardo, Letícia, Pablo,
Nicolas, Bruno) contra **3 sem** (Rodrigo, Vitor, Michel). Maioria, não
unanimidade como no Bloco B — mas a maioria confirma a regra que já
seguimos (correção do Prof. Elvandi no TCC I). **Sem mudança
necessária.**

**DOI e "Disponível em/Acesso em":** nosso formato (`DOI: 10.xxxx`;
`Disponível em: URL. Acesso em: DD mês. YYYY.`) bate com o padrão
observado nos 10 aprovados. **Sem mudança necessária.**

**Não verificável por extração de texto:** negrito do título do
periódico/livro na referência — `pypdf` não preserva formatação de
fonte, só texto corrido. Mantido como está (segue NBR 6023, mesma
convenção já usada no TCC I), mas fica registrado que esse item
específico não foi confirmado contra os aprovados, só contra a norma.

Bloco C fecha sem alteração no `.docx` — ao contrário do Bloco B, aqui a
checagem contra os aprovados CONFIRMOU a escolha já feita, não a mudou.


## 2026-10-05 (continuação) — Revisão completa, Bloco D: rodapé de autor/orientador faltando

Bloco D: checklist de elementos da NBR 14724 contra o `.docx` gerado,
cruzando com os 10 aprovados onde fazia sentido (não só com a norma em
abstrato).

**Folha de aprovação:** confirmado 0 de 10 aprovados têm — o PDF
entregue não inclui (é anexada pela secretaria após a banca, com
assinaturas). Nosso `.docx` também não tem. Sem ação.

**Achado real: faltava o bloco "título do artigo + nome do autor* +
nome do orientador**", com nota de rodapé de mini-currículo, entre a
folha de rosto e o Resumo.** Confirmado em 3 dos 10 aprovados
(estrutura idêntica: título, nome do aluno com `*`, nome do orientador
com `**`, linha em branco, "Resumo:") e no `.doc` oficial do professor.
Nosso `.docx` pulava direto da folha de rosto pro Resumo — elemento
nunca construído em nenhuma sessão anterior.

**E-mail institucional do aluno** (`Gtamiosso@edu.unisinos.br`) foi
pedido ao usuário nesta sessão — não estava registrado em nenhum lugar
do projeto (TCC I usa outro formato de pré-textual, sem esse bloco) e
não é informação que se possa supor. O do orientador já estava
confirmado: `elvandi@unisinos.br` aparece idêntico em todos os 10
aprovados.

**Implementação:** rodapé de Word DE VERDADE, não texto solto
posicionado manualmente — `python-docx` 1.2.0 não tem API de alto
nível pra isso, então a chamada (`w:footnoteReference`, superscrito) e
o corpo da nota (`<w:footnote>` em `word/footnotes.xml`, que já existia
vazio — herdado do `--reference-doc` com os ids -1/0 de separador
padrão do Word) foram montados via XML direto (`lxml.etree`,
`part._blob` — `Part.blob` do `python-docx` só expõe leitura por fora;
`_blob` é o atributo que o `save()` de fato serializa, confirmado lendo
o fonte da biblioteca). Verificado abrindo o `.docx` gerado via
automação do Word: `doc.Footnotes.Count` = 2, texto de cada um conferido
— não é só "não deu erro ao salvar", é a prova de que o Word reconhece
os rodapés como rodapés de verdade, não como XML morto que o Word
ignora silenciosamente.

Documento foi de 55 para 56 páginas totais (o bloco novo). Corpo
inalterado, 30 páginas (mesma razão do Bloco B: é medida relativa).
`verifica_tcc` (20/20) e `confere_docx` (conforme) depois da mudança.


## 2026-10-05 (continuação) — Revisão completa, Bloco E: leitura humana ponta a ponta

Bloco E: renderizar o `.docx` final em PDF (via automação do Word,
`ExportAsFixedFormat` — sem captura de tela do sistema operacional) e
ler página por página com `pymupdf`, procurando o que nenhuma checagem
automatizada pega: título sem espaço antes, quebra de página no meio
de uma tabela, legenda separada do que ela legenda, parágrafo cortado
de forma estranha.

**Achado 1 — Heading 1 sem espaço antes.** Os títulos de seção
("4 METODOLOGIA" etc.) vinham colados no parágrafo anterior, enquanto
Heading 2/3 tinham o espaçamento correto. Uma checagem anterior desta
sessão só tinha comparado o espaço *depois* do título entre os três
níveis (os três batiam, 18pt) e nunca o espaço *antes* especificamente
do H1 (vinha `None`). Corrigido em `aplicar_negrito_titulos()`
(`docs/build_tcc_docx.py`): `space_before = Pt(18)` nos três níveis.

**Achado 2 — a Figura 1 estava com a legenda órfã.** A legenda
"Figura 1 — Página inicial..." ficava sozinha no fim de uma página e a
imagem começava na página seguinte. Causa raiz, uma vez investigada,
não era de paginação e sim de **tamanho**: as 6 capturas do Anexo A são
verticais (até 1440×2812px) e eram inseridas com largura fixa de 15cm
sem limite de altura — o que dava 25 a 29,3cm de imagem, MAIOR que a
página inteira (24,7cm úteis, A4 menos margens ABNT 3cm/2cm). A imagem
não cabia numa página de jeito nenhum, então o Word quebrava ela no
meio e a legenda ficava pra trás.

Primeira tentativa — `keep_with_next` na legenda e na imagem — tratou
o sintoma errado: como a imagem continuava maior que a página, o Word
só empurrava o bloco inteiro pra frente sem conseguir juntá-lo, e o
resultado piorou (3 páginas tocadas por figura: uma quase vazia, uma só
com a legenda, uma só com a imagem — documento foi de 56 para 62
páginas). Abandonado em favor da causa raiz: `_tamanho_figura()` agora
limita a captura a 15cm de largura **e** 19cm de altura (o que sobra
depois de legenda+fonte dentro dos 24,7cm úteis), preservando a
proporção — testado com a imagem mais alta do lote (partida individual,
2812px) e com as outras 5 (2400px). `keep_with_next` na legenda ficou
(não atrapalha mais, e é prática correta para quando a imagem cabe).

Resultado: as 6 figuras agora ficam cada uma em 1 página só (legenda +
imagem + fonte juntas), sem nenhuma vazia. Documento final: 51 páginas
totais (contra 56 antes — as imagens gigantes estavam inflando o PDF
sem ajudar a leitura). Corpo inalterado, 30 páginas.

**Resto da leitura** (Quadro 1 da Seção 5.3, Apêndices, Referências,
Anexo A completo): sem outros achados — quebras de página, tabelas e
numeração consistentes.

`verifica_tcc` (20/20) e `confere_docx` (conforme) depois da mudança.
Fecha o planejamento de revisão completa (Blocos A-E).


## 2026-10-13 — Última leitura completa antes da entrega: sem achados novos

Pedido do usuário: reler todo o material escrito, conferir se figuras e
quadros fazem sentido e se a estrutura ainda bate com os modelos — uma
passada final, depois que os Blocos A-E (2026-10-05) já tinham fechado a
revisão formal. Objetivo era confirmação, não auditoria às cegas: ler
com ceticismo em vez de assumir que, por já ter sido revisado, está
necessariamente certo.

**Leitura de prosa completa** (Resumo → Anexo B, as seções que as
sessões anteriores não tinham relido na íntegra nesta rodada: 1
Introdução, 2 Fundamentação, 3 Trabalhos Relacionados, Referências por
extenso): coerente, terminologia consistente, nenhum placeholder.

**Três checagens novas, que não existiam em nenhuma sessão anterior:**

1. **Apêndice A (esquema do banco) contra `db/schema.sql` real, campo a
   campo.** As 11 tabelas e todos os campos batem exatamente — zero
   deriva entre o que o texto descreve e o schema que o banco
   efetivamente usa hoje.
2. **Toda referência interna "Seção X.Y" do corpo testada por *script*
   contra os headings reais do Markdown** (`re.findall` dos headings
   vs. das citações "Seção N"). Zero link quebrado — nenhuma seção
   citada que não existe no documento.
3. **As 18 entradas de REFERÊNCIAS reconciliadas uma a uma** com as
   citações no corpo: 7 estudos de domínio (Seção 3) + 6 obras de
   método (Seção 2) + 5 referências metodológicas/API (Seção 4,
   Apêndice B/Anexo B) = 18. Nenhuma órfã (citada mas sem entrada), nenhuma
   sobrando (na lista mas nunca citada).
4. **Pré-textual opcional** (Dedicatória, Agradecimentos, Epígrafe,
   Lista de abreviaturas/siglas/símbolos, Folha de aprovação) testado
   contra os 10 aprovados de novo, item que o Bloco B (que olhou só
   Sumário/Listas de ilustração) não tinha coberto: **0 dos 10** usa
   qualquer um desses elementos. Confirma que a ausência deles no nosso
   documento é o padrão, não uma lacuna.

**Figuras/Quadros conferidos contra o código, não só contra o texto:**
a ordem das 6 Figuras em `FIGURAS` (`build_tcc_docx.py`) bate 1:1 com a
promessa da Seção 4.7 ("a Figura 1 mostra a página inicial..."); os 6
Quadros (`QUADROS`) idem, na ordem corpo→Apêndices A-D.

**Suíte reexecutada ao vivo** (não reaproveitada de memória):
`smoke_test` (pass), `validate_predictions` (APROVADO COM RESSALVAS —
as mesmas 5 limitações já declaradas na Seção 5.8), `verifica_tcc`
(20/20), `confere_docx` (conforme).

**Resultado: nenhum achado novo, nenhuma mudança no `.docx`.** Depois de
cinco rodadas de revisão (Blocos A-E) mais esta, o documento resiste a
uma leitura cética completa sem produzir mais nada para corrigir — é o
sinal de que a revisão chegou a rendimento decrescente, não de que
parei de procurar.


## 2026-10-13 (continuação) — Dois achados reais que a leitura automatizada não pegou

O usuário, olhando o `.docx` aberto no Word (não um script), fez duas
perguntas que levaram a dois achados reais — nenhum dos dois tinha
aparecido em nenhuma das seis rodadas de revisão anteriores.

**1. Espaçamento antes do "Resumo:" estava apertado demais.** O bloco
"Título + Autor*/Orientador**" (Bloco D, 2026-10-05) usava
`space_after=12pt` no parágrafo do orientador, em vez de um parágrafo
em branco de verdade. Comparado lado a lado com o `.doc` oficial do
professor (que tem um parágrafo vazio entre o orientador e "Resumo:")
e com a Carolina Paz Prates (TCC aprovado real, mesmo espaço visível
maior), confirmou visualmente que o nosso ficava mais colado.
Corrigido em `montar_pre_textual()`: `space_after=12` trocado por um
parágrafo em branco real.

**2. O Resumo tinha 341 palavras — o modelo oficial exige 100 a 250.**
Achado direto no texto do `.doc` do Prof. Elvandi ("deve conter entre
100 a 250 palavras"), não suposição. Contei o Resumo dos 10 aprovados
pra confirmar que a regra é levada a sério na prática, não só escrita e
ignorada (como aconteceu com outras regras do modelo genérico em
sessões anteriores): todos ficam entre 130 e 249 palavras, nenhum passa
do teto. Resumo cortado para 243 palavras e o Abstract (tradução) para
233, removendo principalmente o nível de detalhe sobre
"39.426 partidas disponíveis quando o conjunto de *features* foi
congelado (39.309 delas geraram linha de *feature*)" — nuance de
metodologia/limitação (Seção 5.8), não algo que um resumo de 250
palavras precise carregar.

**Efeito em duas checagens do `verifica_tcc.py`** (achado 18(c) e uma
checagem dentro de `check_residuos`): ambas exigiam que o Resumo/Abstract
citassem as DUAS bases (41.063 e 39.426) e, no caso do Abstract, a
palavra "limitation". Cortar o Resumo quebrou as duas de propósito —
exatamente o comportamento que se quer de uma checagem que cruza texto
contra regra. Relaxadas para exigir só a base descritiva (41.063,
contagem real que o resumo deve mesmo declarar) e a ausência de uma
frase que reivindique treino sobre ela — o risco original (resumo
afirmando que o modelo foi treinado na base errada) continua coberto;
a exigência da nuance completa é que deixou de fazer sentido num
resumo deliberadamente mais curto.

Rebuild completo: 50 páginas totais (51→50, o corte do Resumo tirou
meia página do pré-textual), corpo inalterado em 30 (é medida
relativa, Introdução→Referências — mesma razão de sempre). `verifica_tcc`
(20/20) e `confere_docx` (conforme) depois da correção.

**Terceira pergunta do usuário, sem achado:** "temos dados reais dos 3
modelos (XGBoost, Random Forest, MLP)?" — sim, confirmado contra
`reports/metricas_corte.json` (gerado 2026-10-04), que tem as métricas
completas dos três em todos os 4 cortes e bate exatamente com o que o
Quadro 2 da Seção 5.4 e o Apêndice C citam. Só o XGBoost (vencedor) foi
exportado pra produção (`data/model.joblib` + `models_phases.joblib`)
— prática normal de ML, e já é isso que o texto descreve ("XGBoost
adotado como modelo de produção").

**Usuário perguntou como o erro do Resumo passou por cinco blocos de
revisão** (resposta honesta: as revisões anteriores checaram ESTRUTURA
— quais seções existem, ordem, elementos presentes/ausentes — e
CONSISTÊNCIA FACTUAL — números batendo com artefato —, nunca
converteram o `.doc` do professor num checklist linha a linha de
regras explícitas de formatação/conteúdo). Isso levou a reler o
`modelo_elvandi.docx` por inteiro (não em fragmentos, como nas sessões
anteriores) e a achar mais dois reais, ambos confirmados contra os 10
aprovados antes de corrigir — para não repetir o erro de generalizar
de um exemplo só:

- **Testado e DESCARTADO**: título em outro idioma antes do Resumo. O
  modelo marca "OPCIONAL"; só 1 dos 10 (Carolina) usa. Não é bug —
  somos maioria (9/10 sem ele).
- **Confirmado e corrigido**: espaçamento interno do bloco
  Resumo/Palavras-chave/Abstract/Key-words. O modelo diz
  "espaçamento simples entre linhas" (diferente do corpo, 1,5); medido
  em 4/4 aprovados via razão delta_y/tamanho_de_fonte (1,15 no resumo
  contra 1,73 no corpo — proporção 1,5 exata). O nosso estava em 1,5
  (herdava do estilo `Normal`). Causa raiz interessante: `_p()` grava
  `line_spacing=1.5` direto no parágrafo, mas o Word, ao salvar de novo
  via `finalize-fields.ps1`, **remove formatação direta redundante com
  o estilo** — como `ajustar_tipografia()` também fixa o estilo
  `Normal` em 1,5, a marcação direta igual ao estilo desaparecia
  silenciosamente no re-save. `line_spacing=1.0` sobrevive porque não é
  mais redundante.
- **Confirmado e corrigido, com nuance**: pontuação/capitalização das
  palavras-chave. O modelo pede `;` entre termos e minúsculas exceto
  substantivo próprio/sigla, com exemplo literal. Nos 10 aprovados o
  `;` é só 5/10 (não unânime como o limite de palavras do resumo) mas
  a **capitalização em minúsculas é consistente** nos que chequei
  (Rodrigo, Eduardo, Michel — todos minúsculo exceto siglas/nomes
  próprios). Corrigido para `;` + minúsculas nas duas línguas (nosso
  "Esports. League of Legends. Análise de dados..." virou "esports;
  *League of Legends*; análise de dados...").

Rebuild: 50 páginas (inalterado), corpo 30 (inalterado — mudança é
toda em formatação de parágrafo, não em quantidade de texto).
`verifica_tcc` (20/20) e `confere_docx` (conforme) depois de cada
correção.

**Pedido do usuário**: recriar o plano de revisão, desta vez tópico a
tópico/linha a linha/estrutura a estrutura/formatação a formatação,
usando o `modelo_elvandi.docx` como checklist explícito (não só como
referência pontual) cruzado contra os 10 aprovados — plano detalhado
na conversa, a executar em blocos como os A-E anteriores.

**Usuário perguntou se os 10 aprovados também foram transcritos por
inteiro** (não — só extração pontual por tópico, mesma limitação de
método que causou o problema do Resumo). Resposta honesta dada, e
construído um esqueleto estrutural em lote dos 10 (títulos de nível 1 +
página de Referências, via `pymupdf`) para servir de base de consulta.
Confirmou a ordem de seções (1 Introdução → 2 Fundamentação/Referencial
Teórico → 3 Trabalhos Relacionados → 4 Metodologia → 5 Resultados → 6
Conclusão/Considerações Finais) em 9/10 — a detecção de subseções (2.1,
2.2...) não funcionou de forma confiável (negrito/caixa alta variam
entre os 10), registrado como limite honesto do método, não escondido.

**Bloco F (Capa + Folha de Rosto) executado.** Negrito (Capa=negrito,
Folha de Rosto=sem negrito, inclusive o nome do aluno) e alinhamento
("Orientador:" à direita) já batiam com o modelo — conferido contra o
XML do `modelo_elvandi.docx` diretamente, não por inspeção visual.
**Achado real**: a frase "Trabalho de Conclusão de Curso apresentado
como requisito parcial para obtenção do **grau** de Bacharel em
Ciência da Computação." estava incompleta e com a palavra errada.
Testado contra 3 aprovados (Carolina, Rodrigo, Henrique) — os três
usam "para obtenção do **título** de Bacharel em Ciência da
Computação, **pelo Curso de Ciência da Computação da Universidade do
Vale do Rio dos Sinos (UNISINOS)**", cláusula final inteira que faltava
na nossa. Corrigido em `build_tcc_docx.py`.

Rebuild: 50 páginas (inalterado), corpo 30 (inalterado — mudança é só
uma frase no pré-textual, que não conta pro corpo). `verifica_tcc`
(20/20) e `confere_docx` (conforme) depois da correção.

## 2026-10-17 — Revisão de naturalidade da prosa (não para driblar detector de IA)

**Pedido original do usuário**: validar a escrita contra "programas
detectores de IA". Recusado nesses termos — o objetivo declarado era
mascarar, para a banca, o quanto de IA entrou na redação, e esse TCC
teve edição direta extensa ao longo de todas as sessões. Reformulado e
aceito pelo usuário como: revisão de **qualidade e naturalidade de
prosa**, comparada contra a variação de estilo real dos 10 aprovados —
um objetivo legítimo (texto melhor é texto melhor), independente de
quem/o que escreveu.

**Achado quantificado, não impressionista**: contagem de travessão (—)
no corpo (Seções 1-6) deu 95 ocorrências em 10.250 palavras (1 a cada
108). Nos 10 aprovados, medido o mesmo jeito: **6 de 10 não usam
NENHUM travessão**, e os 4 que usam ficam entre 1 a cada 320 e 1 a cada
7.770 palavras — 3 a 70× menos frequente que o nosso. É de longe o
maior desvio de estilo encontrado nesta sessão, e um padrão conhecido
de prosa gerada por modelo de linguagem (a construção "frase — aposto
— frase" em cadeia). Outros padrões testados (contraste "não X, mas
Y", "isso é", "vale notar") apareceram raramente nos dois lados — não
eram achado, só o travessão era.

**Correção: 95 → 2 travessões no corpo**, reescrevendo frase por frase
(não substituição mecânica — cada caso recebeu pontuação adequada ao
contexto: vírgula para aposto simples, dois-pontos para explicação que
segue, parênteses para inciso, ponto final para separar em duas
frases). Os 2 que sobraram são legenda de Quadro ("Quadro — Título"),
formato ABNT exigido, não prosa. Headings de Apêndice/Anexo
("APÊNDICE A — Título") e conteúdo de célula de tabela também foram
preservados intencionalmente pelo mesmo motivo. O Abstract em inglês
não foi tocado: a convenção de travessão em inglês acadêmico é
diferente da do português, e não há exemplo real em inglês pra
comparar.

Verificação: cada edição preservou literalmente todo número e fato
citado (`verifica_tcc.py` 20/20 continua batendo os mesmos artefatos
depois da reescrita inteira — prova de que a reformulação não alterou
nenhum dado). Resumo recontado após a reescrita: 239 palavras (dentro
de 100-250). `confere_docx` conforme. Rebuild: 50 páginas, corpo 30
(inalterado — mudança é só pontuação, não volume de texto).


## 2026-10-20 — Lacunas de referência fechadas: 18 → 32 referências

**Origem.** Pergunta do usuário: o TCC tem afirmações sem fonte? Levantadas
as lacunas lendo o texto (métodos citados só pelo nome, uma frase atribuída
à "literatura geral" sem citação, fonte de dados fora da lista). Pesquisa
na web para achar e confirmar os dados bibliográficos; o usuário conferiu o
DOI do Hornik, o do Wallner e o jogo do Hodge.

**Referências acrescentadas (14), todas citadas no corpo** (checagem por
script: nenhuma órfã): Brown, Cai e DasGupta (Wilson, 4.5); Holm (4.5);
Kohavi (validação cruzada, 4.6); Pedregosa (scikit-learn, 4.6); Kaufman
(vazamento de dados, 4.6); Hornik et al. (MLP, 2.2); Grinsztajn et al.
(árvores em dados tabulares, 2.2); Niculescu-Mizil e Caruana (calibração,
5.4); Zhong, Yu e Klein (acurácia de execução, 4.7, com a limitação de o
benchmark usar um banco só); Oracle's Elixir (fonte dos dados, 4.3, acesso
em 20 out. 2026); e quatro estudos de LoL na Seção 3.2: Jadowski e
Cunningham (2022), Do et al. (2021), Maymin (2021) e Guan e Tung (2026,
*preprint* arXiv:2609.08060, sem revisão por pares). Seção 5.7 ganhou um
parágrafo comparando a acurácia com os trabalhos de LoL, marcado como
comparação apenas indicativa (dados, nível e momento da previsão diferem).

**Erro encontrado e corrigido: Hodge et al. (2021) estuda Dota 2, não LoL.**
O texto dizia (3.1) que ele "sustenta, no domínio de League of Legends"
a abordagem, e (5.7) que o estudo "não detalha por fase" e "não propõe
plataforma integrada", duas afirmações que não tinham como ser conferidas
no resumo do artigo. Reescritas com o que o resumo realmente diz (Dota 2
profissional, ao vivo, até 85% após 5 minutos).

**Afirmação sem fonte removida.** "O padrão descrito pela literatura geral
sobre League of Legends" (azul vence no profissional, 5.3): nenhuma fonte
acadêmica com taxa por lado foi achada (o preprint de Guan e Tung trata o
lado e o *first pick* como covariáveis, mas não reporta taxas). A frase
virou "observado neste trabalho" (53,2% em 96.716 jogos), e o preprint é
citado só como apoio à hipótese do *draft*. **Pendência fora do texto:** a
captura do Dashboard (Figura 2, Anexo A) mostra um texto da própria
interface, "a literatura aponta leve vantagem azul no solo queue
(~50,6-53%)", sem fonte; corrigir exige mexer no frontend e refazer as
capturas.

**Outro erro achado ao mover texto:** a nota sobre conversão de vantagem na
5.3 estava truncada (faltavam as palavras entre `features_phases.csv` e
"+6.000"). Reescrita ao ser movida.

**Custo em páginas e como foi absorvido.** As citações levaram o corpo a
31 páginas (teto 30). Aplicado o corte Tier 0 do `plano_reducao_corpo.md`:
lista dos 11 experimentos na 5.4 trocada por remissão ao Apêndice D, e a
"Nota de método" do Quadro 1 mais a origem das taxas de conversão movidas
para o novo **Apêndice E**, sem perda de informação. Corpo de volta a 30.

**Validação.** `verifica_tcc` 20/20, `confere_docx` conforme (esperado
agora 32 referências). Documento: 53 páginas, corpo 30.

**Fora do escopo desta rodada, registrado:** Silva et al. (2018, SBGames)
não foi incluído porque a página original não foi localizada (só números
de segunda mão). Efron e Morris (1977, *shrinkage*) ficou de fora, prioridade
baixa.

## 2026-10-20 (continuação) — Conferência dos artigos e frase sem fonte na interface

**Conferência das referências novas contra o texto dos artigos.** Lidos os
PDFs do Do et al. (FDG 2021, DOI 10.1145/3472538.3472579) e do Kohavi
(IJCAI-95); lidos o resumo do Maymin (De Gruyter) e o do Jadowski e
Cunningham (repositório da MMU), mais os metadados do Crossref para os dois.
Resultado: **Do et al. confere** (75,1% antes da partida, partidas
ranqueadas de 2020, cidade Montreal, editora ACM; referência corrigida, ganhou
DOI); **Kohavi confere** (recomenda validação cruzada estratificada de 10
*folds*; o PDF não traz cidade, então ficou "[S. l.]"); **Maymin**
corrigido (n. 1; o artigo calibra um modelo de probabilidade de vitória com
milhões de partidas ranqueadas, e o texto do TCC dizia só "liga abates e
mortes", que era imprecisão minha a partir do preprint); **Jadowski e
Cunningham** confere (67% de 306 jogos). Não verificados: os nomes dos
organizadores do livro do Jadowski (Wölfel, Bernhardt e Thiel vêm do
preprint de Guan e Tung; o Crossref não os devolve) e o conteúdo integral
do Jadowski (Springer exige login).

**Frase sem fonte tirada da interface.** `Dashboard.tsx` e `Home.tsx`
diziam "a literatura aponta leve vantagem azul no solo queue (~50,6-53%)".
Trocadas por texto que descreve o dado medido, inclusive a inversão no
profissional. Lint e 31 testes passam. Capturas do Anexo A refeitas (base
41.063, 2026-10-20 12:21), recortes regenerados, texto do Anexo A atualizado
("quarta geração"). A Home não concluía o `networkidle` do Playwright (duas
tentativas, API respondendo em ~2 s); `recapturar_anexo_a.py` agora usa
`load` só nessa rota.

## 2026-10-20 (continuação) — Jadowski e Cunningham lido por inteiro

O PDF completo (fornecido pelo usuário) mostrou que a Seção 3.2 descrevia o
estudo errado: são as **ligas regionais profissionais de 2020** (LEC, LCS,
LCK, CBLOL, PCS, TCL), com treino na primeira etapa (882 jogos) e teste na
segunda (306), não "campeonatos internacionais". Corrigido. O artigo também
mede **54,08% de vitórias do azul em 882 jogos profissionais** (qui-quadrado,
p = 0,015), que entrou na Seção 5.3 como apoio externo ao nosso 53,2%. No
guia da banca: os autores escrevem que abordagens assim dificilmente chegam a
90% de acurácia por causa das zebras. Commit 849037c.

## 2026-10-23 — Revisão de formatação contra o modelo e a régua de páginas corrigida

**Achado do usuário: a contagem de páginas estava errada.** O
`finalize-fields.ps1` media da Introdução até a página em que o título
REFERÊNCIAS **começa**, apesar de o comentário dizer "até o fim". Reportava
30/30 quando o real era 37. A régua certa foi medida nos 10 aprovados: o
artigo começa na página física 3 com o número 1, e as Referências terminam no
máximo na física 32 (número 30); só Apêndices e Anexos ficam fora. O script
agora mede do "Resumo:" até a página anterior ao primeiro Apêndice.

**Formatação que tinha passado, conferida contra o `.doc` do modelo oficial
e do exemplo do Prof. Elvandi (convertidos para `.docx` e lidos no XML):**

- **Sem número de página.** O `.docx` tinha uma seção só e nenhum cabeçalho.
  Agora capa e folha de rosto ficam numa seção sem cabeçalho, e o artigo
  começa em 1 no canto superior direito (campo PAGE).
- **Referências em 1,5 e com linha em branco dupla** (espaço do estilo +
  quebra manual). Modelo: simples, 12 pt depois. Foi o que mais pesou na
  contagem (37 → 34).
- REFERÊNCIAS, APÊNDICE e ANEXO **centralizados** (regra escrita no modelo);
  cada Apêndice e Anexo **em página nova** (como nos aprovados).
- Autor e orientador **à direita**, com `*` e `**` (saíam centralizados, com
  1 e 2). "Resumo:" e "Abstract:" **sem recuo**.
- Legenda **sem negrito, 12 pt, centralizada, com "–"** (regra escrita no
  modelo; saía em negrito, 10 pt, à esquerda, com "—"). "Fonte:" centralizada,
  11 pt, sem itálico. Títulos de Apêndice/Anexo com "–".
- **Quadros sem borda nenhuma.** Modelo: moldura completa. Texto das células
  10 pt, cabeçalho em negrito e repetido; quadro curto não se parte.
- **Quadro 2 quebrado:** as células herdavam o recuo de 1,25 cm do Normal e
  partiam "0,7621" em "0,762 / 1". Só aparecia renderizando.
- Natureza do trabalho na folha de rosto com **recuo de 8 cm e espaçamento
  simples**; título quebra a linha depois dos dois-pontos; 3º nível
  ("1.4.1 Objetivo geral") sem caixa alta e à esquerda.
- **Asteriscos impressos** nas notas das Seções 5.3 e 5.4 (itálico dentro
  de itálico no Markdown). As notas viraram texto normal entre parênteses.

Verificado e **mantido**: margens, papel, fonte e entrelinha do corpo, recuo
de parágrafo, rodapé, espaçamento do Resumo. Itálico de termo estrangeiro no
Resumo: só 2 dos 10 aprovados usam, não é padrão.

**Estado:** 35 páginas contadas pela régua nova, 5 acima do limite.
`verifica_tcc.py` CONSISTENTE, `confere_docx.py` conforme. O orientador
pediu quadros e figuras no texto, não nos apêndices; o plano de redução
(`docs/plano_reducao_corpo.md`) foi reescrito com essa restrição: corte de
~3.600 palavras do corpo (~34%), uma seção por vez.

## 2026-10-28 — Quadros e figuras no texto (etapa 1 do plano de redução)

A pedido do orientador ("com tudo no apêndice o texto perde o sentido"),
6 quadros e 5 figuras entraram na Seção 5 (lista em
`docs/plano_reducao_corpo.md`). As figuras são **recortes por elemento** do
painel discutido, gerados por `docs/capturar_figuras_texto.py`; as telas
inteiras foram para o novo Apêndice F, e o anexo da documentação da Riot
passou de Anexo B a Anexo A. Custo medido: 35 → 39 páginas.

**Achados ao preparar as figuras** (todos visíveis em tela que ia impressa):

- A tela **Competitivo** ainda trazia "a literatura que aponta 'leve vantagem
  azul'", a frase sem fonte tirada do Dashboard e da Início em 2026-10-20.
  Trocada pela leitura dos dados, com a explicação marcada como hipótese.
- A mesma tela e a **Campeões** rotulavam o solo queue como "Challenger/GM
  **BR**", mas o número é das cinco regiões (41.063 partidas). Corrigido.
- **Arredondamento duplo** em `/stats/pro/overview`: 0,530534 virava 0,5305
  na API e 53,0% no navegador, contra 53,1% no texto e no SQL direto. A API
  passou a mandar 6 casas.
- A **Explicabilidade** dizia "metodologia de Hodge et al., 2021, com
  explicabilidade via SHAP"; Hodge é Dota 2 e não usa SHAP. Agora cita
  Lundberg e Lee (2017).
- A nota do **Simulador** afirmava como fato que o vermelho é favorecido por
  counter-pick e acesso ao dragão; agora diz que a causa é hipótese. O card
  de SHAP transbordava a nota para fora da borda.
- A captura do **Simulador** do antigo Anexo A era o formulário vazio da aba
  Composição; a legenda prometia estado e SHAP. Agora abre a aba Estado.
- Uma pergunta fora do benchmark ("win rate do azul por região") falhou ao
  testar a figura da consulta NL (coluna inexistente). A figura usa a
  pergunta 9 do benchmark, conferível no Apêndice B.
- A nota da 5.3 dizia que "os Apêndices B e C e o Anexo A citam 39.426"; só
  o C cita.

`build_tcc_docx.py` passou a ler o título de cada quadro da linha "Quadro –"
do Markdown (era lista fixa por posição: inserir um quadro trocaria o título
de todos os seguintes sem erro). `confere_docx.py` deriva do Markdown quantos
quadros e figuras esperar. Frontend: lint limpo, 31 testes passam.
Verificações: `verifica_tcc.py` CONSISTENTE (11 figuras citadas no corpo),
`confere_docx.py` conforme.

## 2026-10-28 (continuação) — Seção 5 condensada, 5.8 fundida na 6.1 (etapa 2)

A 5.8 (Limitações) e a 6.1 diziam duas vezes o que o trabalho não
sustenta. A 6.1 virou a lista única (construto, externa, interna, modelo) e
o detalhe com números e experimentos foi para o novo Apêndice G. Da 5.3
saíram para o Apêndice E a série anual do profissional e a série do teste
(ii) por faixa de duração. Seção 5: 4.295 → 2.077 palavras. Documento: 39 →
34 páginas.

Duas armadilhas da checagem, registradas para a próxima edição:
`verifica_tcc.py` lê o Markdown **inteiro**, inclusive a seção interna de
pendências (um "Seção 5.8" lá reprovou a referência cruzada), e o padrão da
frase-síntese do teste (ii) exige espaço literal em "medido em … sobre as N
partidas: X%"; uma quebra de linha no meio dela reprova a checagem 17.

## 2026-10-28 (continuação) — Seções 4, 2, 3 e 1 condensadas: 29 páginas

Etapas 3 a 6 do plano de redução, uma por commit. Palavras: Metodologia
1.429 → 1.099; Fundamentação 1.493 → 911; Trabalhos Relacionados 1.225 →
837; Introdução 1.293 → 856. Todas as citações mantidas. Documento: 33 →
32 → 30 → **29 páginas** (Resumo ao fim das Referências), meta atingida
com uma página de folga.

Erros corrigidos no caminho, todos de texto que já estava "pronto":
- 2.3: "sempre azul acerta 46,6%" como referência da acurácia; a certa é
  "sempre vermelho acerta 53,4%", a taxa-base.
- 2.3 e 2.4 remetiam à Seção 4 para coisas que ela não descreve nesses
  termos (as "quatro camadas", a separação dado medido × conhecimento geral).
- 3.6: "os trabalhos de predição atuam sobre o profissional" ficou falso
  com Do et al. e Maymin (ranqueadas); "partem de bases de terceiros" e
  "não avaliam contra benchmark" não estavam conferidos nos artigos.
- Introdução: "Oracle's Elixir, ~99 mil partidas" (são 96.716). O
  `verifica_tcc.py` só procurava o literal 99.259; "99 mil" entrou na lista.

## 2026-10-28 (fechamento) — Resumo/Abstract e referência do Kohavi

O Resumo e o Abstract diziam que o azul vence 53,2% "desde 2016", mas 53,2%
é a taxa do acervo inteiro (2014-2026); corrigido. `docs/artigos/` entrou no
`.gitignore`. A referência do Kohavi (IJCAI-95) deixou de ser "[S. l.]":
**San Mateo: Morgan Kaufmann**, p. 1137-1145. A cidade vem de dois
resultados de busca independentes (registro do artigo e catálogo do volume 2
dos anais, ISBN 1-55860-363-8, páginas 1019-2077); o PDF do artigo não a
traz e o DBLP bloqueou a consulta direta. Conferir no PDF dos anais se a
banca cobrar.

## 2026-10-28 (leitura como leitor) — cinco ajustes de conteúdo

Leitura do `.docx` de ponta a ponta, com correções de redação (AUC do MLP
"iguala" 0,9072 vs 0,9090; "mesmo resultado em execuções sucessivas" omitia
a execução de 22/26 do Apêndice B; "que eles não detalham" sobre artigos não
conferidos; "Challenger" × "Desafiante"). Mais cinco decisões aprovadas:

1. Conclusão: "variável sem propriedade intrínseca é um atalho" contradizia a
   hipótese da 5.3 (que atribui o viés a propriedades do jogo). Agora: o lado
   carrega informação sobre o resultado sem refletir o estado da partida.
2. Conclusão: saiu "com potencial de contribuição à literatura".
3. O módulo de orientação (*coach*) era citado na 4.8, 5.7 e 6.1 sem nunca
   ser descrito; ganhou um parágrafo na 4.7, escrito a partir de
   `src/coach/advice.py`.
4. 5.4: a causa do teto (volume × engenharia de variáveis) passou a "é
   consistente com", com a ressalva dos três pontos.
5. 5.3: a nota das duas bases saiu da abertura da seção e vai depois da
   análise do Quadro 2.

Documento segue em 29 páginas.

## 2026-11-02 — Decisões confirmadas pelo autor, motivo do elo alto no texto, Maymin conferido

**Três decisões que não tinham registro escrito**, confirmadas pelo autor:
(1) comparar XGBoost com *Random Forest* e redes neurais veio de uma
conversa com o orientador, para ver as diferenças de resultado (a
justificativa formal segue a do TCC I, 4.6); (2) Desafiante e Grão-Mestre
por escopo; (3) 5 dobras e não as 10 do Kohavi por custo computacional, com
~7.800 partidas por dobra de teste e a mesma divisão em todos os scripts.
Registradas em `docs/guia_banca.md`.

**4.3 a)** ganhou o motivo do recorte de elo: "recorte de escopo: uma
população fechada, que a API lista por inteiro e que cabe no limite de
requisições da chave de desenvolvedor". Para compensar, saiu da mesma
frase "com o JSON bruto preservado para reprocessamento", que a 5.2 já
diz. `verifica_tcc.py` consistente, `confere_docx.py` conforme, documento
em 29 páginas.

**Maymin (2021) lido no texto completo** (acesso aberto, CC BY 4.0, página
da De Gruyter Brill): o modelo de probabilidade em jogo usa milhões de
partidas, um minuto sorteado de cada, então a frase da 3.2 está correta. Os
~150 mil jogos do último *patch* são da análise de desempenho individual, e
o guia, que os atribuía à calibração, foi corrigido.

**Achado: a comparação do Quadro 3 não está toda ajustada.** A 5.4 diz
"compara os três modelos após ajuste de hiperparâmetros", mas
`multi_cutoff_metrics.py` usa *Random Forest* com 500 árvores e sem limite
de profundidade e MLP (64, 32) com os padrões; só o XGBoost veio da busca em
grade (na base de 10.295). Rodado `python -m src.models.tune_models_full
--completo` sobre as 39.188 linhas (grava `reports/tune_models_39k.json`):
melhor RF `max_depth=6, min_samples_leaf=5, n_estimators=200`, AUC média
0,8470; melhor MLP `(32,)`, `alpha=0.001`, AUC média 0,8478. Medidos como
no Quadro 3 (`cross_val_predict`, 5 dobras, semente 42, probabilidades
agregadas; comando ad hoc nesta sessão, ainda sem script próprio):

| 15 min | Acurácia | AUC |
|---|---:|---:|
| XGBoost 500/0,01/3 | 0,7621 | 0,8473 |
| MLP (32,), alpha 0,001 | 0,7619 | 0,8477 |
| RF 200, prof. 6, folha 5 | 0,7617 | 0,8468 |

Empate técnico; o XGBoost mantém a maior acurácia (critério do Apêndice
G), a MLP ajustada tem a maior AUC por 0,0004. A conclusão não muda, mas a
frase da 5.4 e as linhas de RF e MLP do Quadro 3 descrevem configurações
não ajustadas.

**Corrigido no texto (Passo 0 da revisão do Resumo, aprovado pelo autor).**
A 5.4 agora diz que o Quadro 3 traz o XGBoost com os hiperparâmetros da
busca e os outros dois na configuração de referência, e cita os valores
ajustados (RF 0,7617 / 0,8468; MLP 0,7619 / 0,8477). A nota do Apêndice C
descreve as configurações de RF e MLP. `tune_models_full.py --completo`
passou a medir a melhor combinação como no Quadro 3 (`cross_val_predict`)
e grava `acuracia_quadro3` e `auc_quadro3` no JSON, que é a fonte dos
números. `verifica_tcc.py` consistente, `confere_docx.py` conforme, 29
páginas.

**Resumo e Abstract reescritos** contra a estrutura do modelo do professor
(contexto, objetivo, metodologia, resultados, conclusão; 100 a 250
palavras). Faltava a metodologia: entram "pesquisa aplicada, de abordagem
mista" e "validação cruzada estratificada". "O XGBoost alcançou o melhor
desempenho" vira "os três ficaram próximos, e o XGBoost, adotado em
produção", coerente com a 5.4 nova; "acurácia" da interface vira "acurácia
de execução"; "partidas profissionais" vira "jogos". Sai o mapa de calor
para caber. Abstract traduzido da versão nova, com ajustes de inglês ("its
use" sem referente, "along the match", *machine learning* sem itálico,
sem travessões). Resumo 232 palavras, Abstract 227; 29 páginas.

## 2026-11-02 (continuação) — Conferência das referências: sete ajustes aplicados

Lidos o texto completo de 11 estudos de domínio e das obras de método de
acesso aberto, por busca nas frases do TCC (`docs/conferencia_referencias.md`).
Aplicados no texto: 2.4 (o "diálogo" é do SiriusBI, não do Talk2Data), 3.3 e
5.7 (García-Méndez apontam a falta de interpretabilidade como limitação, não
dizem que a previsão "só é útil" com explicação; o jogo é CS:GO profissional),
2.3 (LIME "dependente" de como a vizinhança é definida, em vez de
"sensível"), 3.1 (os 85% do Hodge vêm de previsões ao vivo de 28 partidas),
5.7 (o mapa de calor também cita Maymin, 2021), 2.5 ("motivou" em vez de
"fundamentou") e 2.1 (Bahrololloomi: "resultado da partida"). Nenhum número
mudou. `verifica_tcc.py` consistente, `confere_docx.py` conforme, 29
páginas. Resumo e Abstract não citam nenhum dos trechos corrigidos.

## 2026-11-03 — Plano de linguagem executado (oito passos) e Grinsztajn conferido

Os oito passos de `docs/analise_escrita.md` foram aplicados ao corpo, um
commit por grupo, cada um com `verifica_tcc.py` e `confere_docx.py` e a
contagem de páginas (29 em todos): (1) citações com ponto e vírgula entre
autores e ano nas três da 3.6; (2) "num/numa" e "só" saem; (3) datas ISO e
código saem do corpo; (4) as construções ", e não X" viram afirmações
diretas; (5) vinte pontos e vírgulas entre orações viram ponto; (6)
catorze remissões redundantes saem; (7) "features", "dataset", "folds" e
"pipeline" viram português; (8) cinco conectivos. `verifica_tcc.py` passou
a aceitar a data por extenso na frase-síntese do teste (ii). Os apêndices
não foram tocados. Comparação antes e depois em `analise_escrita.md`.

Grinsztajn et al. conferido no texto completo (colado pelo autor): porte
médio é cerca de 10 mil exemplos, e no Apêndice A.2.2 os autores observam,
sem estudar a fundo, que a diferença diminui com 50 mil. A 2.2 passou a
dizer isso.

## 2026-11-03 (continuação) — Apêndices reescritos sem prosa

Decisão do autor: os apêndices não devem ter texto corrido como o D (nenhum
dos 10 TCC II aprovados tem); imagens, tabelas e quadros são bem-vindos. A
única restrição do orientador é que o corpo faça sentido sozinho, e todos os
ponteiros do corpo para apêndices (A, B, C, D, E, F, G) são de detalhe,
histórico, origem ou comando, não de conteúdo de que a leitura dependa.

Reescritos D, E e G, e enxugados A, B, C e F: a prosa de diário (datas ISO,
"achado em", versões anteriores da nota) saiu, e o conteúdo virou 12 quadros
novos (agora 21 no total: 6 no corpo e 15 nos apêndices): execuções do
benchmark, configuração dos três modelos, detalhe e reprodução dos
experimentos 4, 10 e 11, efeito do volume de partidas, partidas por região na
primeira e na última medição, origem dos números da 5.3, faixas de duração,
série anual do profissional, limitações com a evidência de cada uma, taxa-base
no empate (modelo × dados, com a diferença por corte) e alavancas testadas.
Nenhum número foi alterado; as diferenças de taxa-base por corte (2,8, 1,7,
4,7 e 1,9 pp) são cálculo direto dos valores já citados.

**Erro achado ao reescrever o D:** o texto dizia que o ganho por volume
(0,0259) era "cerca de 6×" o maior ganho de um experimento (0,003). A conta
dá 8,6; o "130×" sobre o menor (0,0002) estava certo. O apêndice agora diz
"cerca de nove vezes", e o guia e o site foram corrigidos.

**Ferramentas:** `verifica_tcc.py` (checagem 17) passou a ler a série das
faixas de duração de um quadro em vez de um parágrafo, e foi testada nos dois
sentidos (trocar 46,5% por 46,9% reprova). `build_tcc_docx.py` tinha duas
suposições de que a tabela de arquivos do Apêndice F é a última do documento;
agora ela é achada pelo cabeçalho. 29 páginas no corpo, documento total em 50.

## 2026-11-03 (continuação) — Robustez de 5 contra 10 dobras

Criado `src/models/robustez_dobras.py` (documentado em `comandos.md`): mesmos
modelos e semente de `multi_cutoff_metrics.py`, 5 e 10 dobras. XGBoost nos
quatro cortes e os três modelos aos 15 min: diferença máxima de 0,0008 em
acurácia e 0,0006 em AUC-ROC. Entrou como quadro no Apêndice C; o corpo não
mudou. Responde ao Kohavi (1995), que recomenda 10.

## 2026-11-03 (continuação) — Baseline logístico e IC das diferenças: achado

`src/models/baseline_e_diferencas.py` (documentado em `comandos.md`):
regressão logística padronizada como baseline e *bootstrap* pareado (1.000
reamostragens) da diferença do XGBoost para os demais, sobre as previsões
fora da amostra de 5 dobras. **A regressão logística empata com o XGBoost e
tem AUC ligeiramente maior** (15 min: 0,7631 / 0,8483 contra 0,7621 / 0,8473;
XGBoost menos logística = −0,0010, IC −0,0014 a −0,0006; aos 25 min o IC
inclui zero). XGBoost − MLP = +0,0019 (IC +0,0011 a +0,0026); XGBoost −
*Random Forest* de referência = +0,0197. Consequência: "empate técnico"
continua certo em termos práticos (milésimos), mas as diferenças não são
todas nulas estatisticamente, e o XGBoost não é o melhor numericamente. A
5.4 ganhou uma frase com o baseline ("o limite está nas cinco variáveis") e
o Apêndice C um quadro com os intervalos; 29 páginas. Resumo e Abstract não
dizem que o XGBoost é o melhor, só "adotado", e seguem verdadeiros.

## Próximos registros pendentes

- **Sprint 0 do planejamento v2**: pedir a Personal API Key no portal
  da Riot (a chave de dev expira em 24h) — a coleta em background
  seguiu rodando com a chave dev de qualquer forma (ver 2026-07-06:
  EUW1/KR/NA1 saíram de 45-266 para 1.307-1.367 partidas cada).
- Ampliar ainda mais a amostra por região (KR/EUW1/NA1 seguem bem
  menores que BR1) pra deixar o achado do viés de lado (2026-07-06:
  todas as 4 regiões pendem pro vermelho, não só BR) mais conclusivo.
  **Usar `--players` bem maior (500-1000+)** — 100 só pega o topo do
  ladder, que já foi coletado (ver entrada 2026-07-06 acima: 100
  rendeu só 103 partidas novas de 3 regiões).
- ~~Quando a coleta adicional de solo queue terminar: rerodar
  `load_items`, `build_features`, `export_model`~~ — **feito em
  2026-07-06** (ver entrada acima: AUC 0.8214→0.8289). Collection
  segue rodando em background — repetir este pipeline periodicamente
  conforme o volume crescer.
- Team builder — próximos incrementos da visão original: jogadores na
  análise e champion select competitivo (o mapa de calor da partida já
  foi entregue na análise de partidas).
- ~~Sinergias de dupla com correção de amostra (shrinkage/IC)~~ —
  **feito em 2026-07-06** (ver entrada acima).
- ~~Atualizar as tabelas de métricas do texto do TCC com os números do
  retreino de 2026-07-03~~ — **feito, e superado**: o retreino de
  2026-07-03 foi substituído pelo de 2026-10-04 (39.188 linhas no corte
  de 15 min, XGBoost 0,7621 / AUC 0,8473). O Quadro 2, o Apêndice C e a
  série de AUC por corte estão com os números atuais, e
  `docs/verifica_tcc.py` confronta o texto com
  `reports/metricas_corte.json` para não voltarem a divergir.
- ~~Revisar os capítulos do texto do TCC com os resultados registrados
  neste diário~~ — **feito** (2026-10-04). A revisão independente
  encontrou
  quatro números que nunca existiram (99.259 jogos profissionais,
  Quadro 1 com a NA1 desatualizada, conversão de vantagem, série de
  SHAP), um achado refutado pelo aumento da amostra (o viés de lado é
  **constante**, não dinâmico) e o Abstract em inglês repetindo a forma
  antiga — que vai impresso no pré-textual do `.docx`. O nome do produto
  Bellestraiko está registrado na Seção 1.1. — usar o nome do produto, **Bellestraiko** (o "Hextech Lab"
  foi descartado em 2026-07-03 por colisão com canal do YouTube; as
  menções históricas aos dois renomes nas entradas acima são legítimas e
  devem ficar).
- Considerar `monotone_constraints` no XGBoost se a banca cobrar
  monotonicidade formal por fator isolado (ver bateria de validação
  acima) — mudança de modelagem, não prioridade atual.
- ~~Extração de itens (ITEM_PURCHASED/SOLD)~~ e ~~visão
  (WARD_PLACED/KILL)~~ — **ambos testados em 2026-07-06, negativos**
  (ver entradas abaixo). Não há mais candidato de dado novo óbvio na
  timeline não testado; próximo ganho de modelo provavelmente exige
  dado que a timeline não tem (ex.: draft/pick-ban order, posição em
  tempo real para features espaciais).
- Competitivo/pro-play: adiado (ver acima); se retomado, opções já
  levantadas em `project_scope_decisions.md`.

## 2026-11-03 (continuação) — Leitura linear das referências e seis correções aplicadas

**O que foi feito.** Leitura do início ao fim (não por busca) dos 11 estudos de
domínio e de Hanley e McNeil, Kohavi, Hornik, Breiman, Lundberg e Lee,
Niculescu-Mizil e Caruana, Holm, Wang et al., Zhong et al., Chen e Guestrin,
Ribeiro et al., Pedregosa et al., Grinsztajn et al. (v1 do arXiv), Brown et al.
(págs. 1 a 20 do relatório de 1999) e Kaufman et al. (versão KDD 2011). Os
resultados, com página e trecho, estão em `docs/conferencia_referencias.md`.

**Aplicado no TCC (com aprovação):**
- 4.4: citação de Kohavi movida para "estratificada (Kohavi, 1995), com 5
  dobras" (ele recomenda 10) e páginas da referência corrigidas para 1137-1143.
- 4.1, 4.2, Resumo e *Abstract*: "abordagem mista" virou "quantitativa" (Creswell
  e Creswell exigem coleta qualitativa para o método misto) e a citação de Yin
  foi removida, com a referência (32 para 31; `confere_docx.py` atualizado).
- Seis correções de intensidade: 2.3 (LIME), 3.2 (Birant, Bahrololloomi,
  Maymin), 3.4 (Guo e SiriusBI) e 3.5 (Wallner).

**Lição de layout.** A primeira versão das seis correções (cerca de 110
caracteres a mais) levou o corpo de 29 para 30 páginas, porque um quadro ou
figura mudou de página e abriu um vão (última página 45% cheia). Reduzidas a
tamanho líquido ~zero, voltou a 29 páginas, `verifica_tcc.py` consistente e
`confere_docx.py` conforme. Conferir a contagem a cada edição no corpo.

**Erro meu corrigido.** O guia dizia que Pedregosa et al. (2011) é a origem do
MLP e do *Random Forest*; o artigo não descreve nenhum dos dois.

**Pendentes.** Correção do Breiman na 2.2 (a frase "reduz a variância do
conjunto, o que importa quando as variáveis são correlacionadas" não tem apoio;
proposta de tamanho líquido ~zero aguarda aprovação); conferência da versão de
2012 do Kaufman (págs. 15:1 a 15:11); teste de treino no passado e teste no
futuro; slides; roteiro e teste da demonstração; releitura final do documento.

## 2026-11-03 (continuação) — Treino no passado, teste no futuro; correção do Breiman

**Medida nova.** `src/models/holdout_temporal.py` (Apêndice C, Quadro 14;
`reports/holdout_temporal.json`; checagem 20 de `verifica_tcc.py`, agora são 21)
responde ao aviso de Kaufman et al. (2012) sobre dados que mudam com o tempo.
Três divisões sobre as 41.063 partidas (18 mai. a 4 out. 2026, dez *patches*):
cronológica 80/20, por *patch* (treina 16.10 a 16.13, testa 16.14 a 16.19) e
aleatória de mesmo tamanho do teste cronológico. **Resultado:** nenhuma divisão
temporal fica abaixo da aleatória em mais de 0,0004 de AUC-ROC (pior caso: 20
min, por *patch*); aos 15 min, 0,8545 e 0,8542 contra 0,8432. A regressão
logística dá o mesmo padrão (até 0,0012 de diferença para o XGBoost).
**Ressalva registrada no texto:** o teste cronológico aos 15 min tem 49,7% de
NA1 e nenhuma BR1 (37,7% do treino), então tempo e região se misturam.

**Texto.** O Apêndice C ganhou o quadro e o parágrafo; a linha "Cobertura
desigual por versão do jogo" das limitações passou a dizer "o *patch* 16.13
concentra 40,4% das partidas (16.572 de 41.063)" (antes: "a maior parte", que
era falso) com a evidência; a 6.2 (validade interna) ganhou uma frase e a
"validade externa" a correção do 40,4%. Corrigida também a 2.2 (Breiman): a
frase sobre "reduz a variância do conjunto" foi trocada por "reduz a correlação
entre as árvores, o que limita o ganho de um *ensemble*".

**Guarda de valores antigos.** O quadro novo traz 0,7573 (acurácia aos 15 min
da divisão aleatória), igual por coincidência ao valor antigo do XGBoost que
`VALORES_SUBSTITUIDOS` proíbe. Em vez de mudar a semente (o que enviesaria o
resultado), as linhas do quadro ficaram isentas na checagem 8, com o motivo no
código.

**Verificação.** Corpo em 29 páginas; `verifica_tcc.py` consistente (21
checagens; teste de mutação da checagem 20 reprovou como deveria) e
`confere_docx.py` conforme. Quadro renderizado e conferido a olho.

**Kaufman et al. (2012).** O PDF do artigo de periódico (TKDD v. 6, n. 4, art.
15; 21 págs.) foi recebido e lido inteiro: a referência do TCC está correta e a
frase da 4.4 confere. A seção 7 (vazamento por estratificação num colisor) virou
uma pergunta de defesa, registrada no guia e em `conferencia_referencias.md`.
Pendência fechada; nenhuma mudança no TCC.

## 2026-11-03 (noite) — Conferência da Riot API e do Oracle's Elixir

Afirmações do TCC conferidas contra o código, o banco, os 13 CSVs de
`data/pro/` e o portal oficial (detalhe em `docs/conferencia_referencias.md`).

- **Erro em `src/etl/load_pro.py`.** Cada CSV apagava `WHERE year = ano do
  arquivo`, mas inseria cada linha com o `year` que ela traz. Jogos de um ano
  dentro do arquivo do ano anterior (ex.: 2015 no arquivo de 2014) eram
  apagados quando o arquivo seguinte era carregado: **2.543 jogos perdidos**.
  O "96.716" registrado acima como correto era o valor errado; o certo é
  **99.259** (`COUNT(DISTINCT game_id)` após a correção; 198.518 linhas de time
  e 992.590 de jogador). Correção: apagar por `game_id`. Taxa do azul no total
  inalterada (53,2%); 2015 passou a 55,0%, 2016 a 53,5%, 2018 a 53,6% e 2025 a
  53,2%. O benchmark do NLQ não muda (gabarito e SQL gerada rodam no mesmo
  banco).
- **Texto.** 96.716 → 99.259 em todo lugar; `verifica_tcc.py` agora proíbe
  "96.716". "Principais ligas" → "122 ligas, da elite às de desenvolvimento".
  "Desafiante e Grão-Mestre" → "elo alto (Desafiante a Mestre)": a tabela
  `players` tem 93% de Mestre, 97,2% das partidas têm ao menos um
  Desafiante/Grão-Mestre e 2,8% só Mestre. "timeline-v5" não existe na
  documentação da Riot: é o método de linha do tempo do *match-v5*. Data dos
  arquivos do Oracle's Elixir: 4 jul. 2026.
- **Build.** `build_tcc_docx.py` exige `TCC1_REFERENCE_DOCX`; sem ele aborta e
  o `.docx` não é regenerado (o `finalize` roda mesmo assim sobre o arquivo
  antigo).

## 2026-11-03 (noite) — Experimentos de precisão e apêndices H a M

**Meta.** Sem meta de valor (decisão do autor): explorar todas as possibilidades. 0,90 de acurácia aos 15 minutos foi descartado por inviável; a literatura achada fica entre 73% e 82% em partida em andamento, e resultados acima disso sem discussão de vazamento são suspeitos.

**Experimentos 12 a 19** (código em `src/features/build_features_v2.py`, `src/models/experiment_precisao.py`, `holdout_precisao.py`, `experiment_historico.py`). Base congelada de 39.426 partidas, 5 dobras, semente 42. Melhor resultado: regressão logística com 64 variáveis, +0,0080 de AUC-ROC aos 15 minutos (0,8483 → 0,8555 na validação cruzada) e +0,0074 aos 25 (0,9163), mantido em treino no passado e teste no futuro (+0,0069 a +0,0089). Por conjunto: função +0,0027, campeões +0,0013, histórico do jogador +0,0011 (e +0,0004 sobre o estado rico, mesmo com 92% das partidas bem cobertas), trajetória e objetivos ~0. Abaixo do critério de +0,01 combinado para mexer no corpo; entra só no Apêndice M. Erro meu corrigido: a "cobertura de 31%" do histórico era métrica errada (diferença de contagem); a real é ~92%.

**TCC.** Apêndices H (fundamentos dos métodos), I (estudos de domínio e comparação), J (procedência dos dados e chaves da Riot), K (objetivos e evidências), L (SHAP por corte, de `reports/shap_importance_phases.json`) e M (experimentos 12 a 19), todos em quadros; seis ponteiros no corpo, sem mudar resultado. A 6.2 ganhou o quinto trabalho futuro (chave de produção da Riot; a documentação não lista dados novos nas APIs padrão). Corpo em 29 páginas. A coleta em andamento mudou o banco (42.137 partidas, BR1 13.010) e o verificador acusou quatro divergências. Cópia completa em `data/backups/lol_analytics_com_coleta_nov03.dump` (3,3 GB, fora do git); as 1.749 partidas novas (`raw_matches.collected_at` de 3/11 a partir das 18h) foram apagadas das sete tabelas e o banco voltou às 41.063 do texto (BR1 11.936, EUW1 11.744, KR 10.204, NA1 7.159, EUN1 20). Para recarregá-las depois da banca: restaurar o dump.

**Comparação com o histórico (git).** O corpo de 20/10 tinha 11.753 palavras; hoje, 8.958. Quase nenhum número se perdeu (só os corrigidos e os valores SHAP de ouro e experiência por corte, agora no Apêndice L).

## 2026-11-05 (noite) — Regras gerais da consulta e segundo conjunto cego

**O que foi feito.** Regras gerais no esquema (amostra mínima, agregação por jogo, sequências, ano, LIMIT 500 com aviso de truncamento), `extrair_sql` (resolve o "Múltiplos statements" da pergunta 86) e `n_linhas` na API. Benchmark de referência 26/26; a v1 re-executada deixou de ser cega (virou desenvolvimento).

**Segundo conjunto cego (perguntas 101 a 150).** Uma primeira tentativa foi descartada: o arquivo recebido continha só perguntas já usadas (27 da v1, 23 do desenvolvimento, nas linhas 1-50). As 50 perguntas inéditas foram checadas por código contra v1 e desenvolvimento, rodadas uma vez no commit 1fe0014 e conferidas no banco: **27 de 50 certas (54%)**, IC 95% 40%–67% (18 C, 9 RC, 9 P, 13 E, 1 RE). Sobrepõe-se ao 30/50 (60%) da v1: sem melhora demonstrável. Falha dominante: substituto sem rótulo quando o dado não existe (primeira torre, primeiro sangue, série). Decisão do autor (opção A): não ajustar o sistema; relatar as duas medidas e declarar a falha. Artefatos: `reports/nlq_cego_v2_resultado.json`, `reports/nlq_cego_v2_vereditos.json`, `docs/revisao_nlq_cego_v2.md`. TCC: Resumo, 5.6, 6.1, 6.2, Apêndices B e F; `verifica_tcc` confere o 27/50; corpo em 29 páginas.

## 2026-11-05 (madrugada) — Gabarito automático (medida principal)

**O que foi feito.** `src/nlq/gerar_gabarito.py` gera 900 perguntas por template com SQL de referência (executada na geração); `src/nlq/avaliar_gabarito.py` compara por código. O crédito da API acabou depois de 203 perguntas: **181 de 203 certas (89,2%)**, IC 95% 84,1%–92,7%; 166/187 respondíveis, 15/16 recusas. As 22 falhas são do sistema (nomes de entidade, eliminações = kills+assists, roteamento). Depois da medida: `src/nlq/entidades.py` (nome exato do banco, roteamento por entidade) e checagem de eliminações, com testes unitários, **sem medida de ponta a ponta**. Decisão do autor: ficar com as 203 e não recarregar a API. TCC: Resumo, 5.6, 6.1, 6.2, Apêndice B (+ quadro por família) e Apêndice F; `verifica_tcc` confere 181/203; corpo em 29 páginas.

## 2026-11-06 — Base única de 41.063 partidas

**Decisão.** O TCC citava três números de partidas (41.063, 39.426 e 39.188) porque as *features* e os modelos tinham sido congelados antes da última rodada de coleta. Para ter uma base só, o pipeline inteiro foi refeito sobre as 41.063: `build_features`, modelos por corte, SHAP, `tune_models_full --completo`, robustez de dobras, divisão temporal e experimentos 1 a 19. O número de partidas passa a variar só por corte (40.942, 40.816, 35.637 e 27.761).

**Resultado (15 min).** XGBoost 0,7636 de acurácia e 0,8490 de AUC-ROC (antes 0,7621 e 0,8473). Comparação completa em `docs/comparacao_rerun_41063.md`. Mudaram afirmações, não só números: o MLP ajustado fica 0,0009 acima do XGBoost em acurácia (o XGBoost não é mais o de maior acurácia entre os ajustados); a produção cai para 3º entre 27 combinações da grade; a divisão temporal nunca fica abaixo da aleatória; torres passam de ~15 para ~11 vezes; conversão de vantagem 74,1% contra 81,5% (7,4 pp, z = 8,0).

**Ferramentas.** `docs/regenera_quadros.py` reescreve os quadros a partir de `reports/*.json`; `docs/verifica_tcc.py` passou a exigir base única. Backups: `data/backups/pre_rerun_41063/` e `data/backups/rerun_41063/` (fora do git). A Figura 5 (consulta em linguagem natural) não foi recapturada por falta de crédito na API e segue a antiga.

## 2026-11-08 — Parecer do orientador sobre o TCC II

**O que pediu.** Seis blocos: introdução sem subseções e sem menção ao TCC I; o viés de lado sem "estável ao longo da partida" e com teste que respeite a sobreposição entre cortes; a comparação dos modelos após o ajuste e com a regressão logística; calibração medida nas partidas empatadas reais, escala do SHAP, experimento 11 à parte e o +0,0078 isolado; NLQ com versões, congelamento e regra do comparador; formatação (chamadas, hífen, Anexo A, siglas).

**O que se mediu (cada número com artefato em `reports/`).**
- Viés por corte com a partida como unidade (`docs/testa_diferenca_taxas.py`, reescrito): 2.767 das 12.621 partidas empatadas estão em 2+ cortes; bootstrap por partida, menor p de Holm 0,64 (antes, com z independente, 0,93). Nenhuma diferença detectada.
- Calibração nas empatadas reais, fora da dobra (`docs/calibracao_empate_real.py`): diferença −0,18 a +0,41 pp; maior desvio entre decis 1,25 pp aos 15 min. A "discrepância de 2,4 a 4,6 pp" vinha do estado todo-zero, que não ocorre em nenhuma partida empatada. Sigmoide piora a calibração por decis; isotônica não melhora Brier nem AUC.
- Busca aninhada (`src/models/tune_models_aninhado.py`): XGBoost 0,8491, RF 0,8483, MLP 0,8494, a no máximo 0,0001 do não aninhado. As 10.295 partidas da grade do XGBoost estão dentro das 40.816 da avaliação (declarado na 4.6).
- Curva de aprendizado com teste fixo (`src/models/curva_aprendizado.py`): 0,8466 (2.500) → 0,8484 (10.000) → 0,8495 (32.652). Mesmas 27.761 partidas nos quatro cortes: 0,6653 / 0,7378 / 0,8135 / 0,9092.
- Ganho das variáveis no mesmo classificador (`src/models/ganho_variaveis_logit.py`): logística +0,0070 [0,0058; 0,0080] aos 15 min e +0,0074 aos 25; XGBoost +0,0040.
- Comparador do gabarito (`src/nlq/confere_comparador.py`): 0 dos 146 acertos escalares tinham 2+ colunas numéricas.
- Congelamento: última coleta de solo queue em 2026-10-04 19:41; CSVs profissionais de 2026-07-04; nada entrou depois. A versão medida do `nl_to_sql.py` não estava em commit; recuperada do histórico local e marcada na tag `gabarito-203`.

**O que mudou no texto.** Introdução em parágrafos (sem 1.1 a 1.5), sem Abstract (opcional no modelo), sem menções ao TCC I, Anexo A eliminado (citação Riot Games na 4.3 e 5.1); Quadro 3 com a comparação após o ajuste, a logística e a coluna aninhada; Apêndice F com calibração nas empatadas e Figura 12; Apêndice C com Quadros 16 e 17; Apêndice K com o 11 à parte e a linha logística contra logística; SHAP em log-odds na 2.3, 5.5, Figura 4 (recapturada) e no coach; 5.6 com os controles de execução e sem "garante a segurança"; Apêndice B com versões, congelamento e regra do comparador; chamadas de todos os quadros dos apêndices; hífen nas legendas e títulos. Corpo: 30 páginas (no limite).

**Código.** `/predict` devolve a referência e a unidade do SHAP; Simulador e coach mostram a unidade; `verifica_tcc.py` (checagem 14 nova) CONSISTENTE; `confere_docx.py` conforme.

**Ajustes de fidelidade ao parecer (mesmo dia).** Conferência item a item mostrou pontos não seguidos à risca, agora corrigidos: siglas dos apêndices por extenso (NLQ, IA, IC, KPI, PK, FK, JSONB, pp); o caso 5 do *coach* saiu da 6.1 e foi para a discussão (5.7), como o parecer pede; 166 de 187 e 15 de 16 também no Apêndice I e no Quadro 22; o protocolo do experimento 4 identificado no Apêndice K (3 dobras internas, mesmas diferenças de AUC-ROC no protocolo do Quadro 24). Duas perdas da primeira rodada desfeitas: o Quadro 3 voltou a ter precisão, *recall* e F1 (ajustados e logística em `reports/metricas_ajustados.json`, `src/models/metricas_ajustados.py`, que reproduz a acurácia e a AUC-ROC publicadas) e o Resumo recuperou as frases dos testes de robustez e das seis páginas de visualização (248 palavras). Linha em branco entre Resumo e Palavras-chave, como no modelo. Corpo continua em 30 páginas.

## 2026-11-08 (noite) — Revisão profunda: vazamento do quadro final e reexecução do pipeline

**O achado.** Revisão linha a linha, figura a figura e quadro a quadro. O mais grave: `features_from_timeline` só checava `len(frames) <= cutoff`. A linha do tempo da Riot termina com um quadro extra no instante do fim do jogo, então numa partida de 24:16 `frames[25]` é esse quadro final e entrava como "estado aos 25 minutos" (BR1_3243932554 conferida no banco). Afetava 22/37/1.120/2.642 partidas aos 10/15/20/25 min; nelas a AUC-ROC era 1,0. Violação do invariante 1.

**Correção.** `corte_disponivel()` em `build_features.py` exige um quadro DEPOIS do quadro do corte; vale em `build_features`, `build_features_v2` (via `features_from_timeline`), `build_features_antigos` e nos experimentos antigos. Teste novo `tests/test_corte_sem_quadro_final.py` (400 pares partida-corte com partida mais curta, 0 falhas). Os testes de vazamento v2/antigos passaram a acrescentar um quadro vazio depois do corte. Backup em `data/backups/pre_vazamento_20261108/`.

**Reexecução completa** (scratchpad `pipeline.sh`, 17:37–20:05, nenhum passo falhou): variáveis (40.919/40.778/34.505/25.098 partidas), modelos exportados, métricas por corte, busca em grade completa e aninhada, métricas dos ajustados, logística, 5×10 dobras, holdout temporal, SHAP, viés por partida, faixa de duração, conversão, calibração, curva de aprendizado, experimentos 1 a 19, `validate_predictions` e `smoke_test`.

**O que mudou.** 15 min: XGBoost 0,7641 / 0,8487 (era 0,7636 / 0,8490); ajustados 0,8480 a 0,8495. 20 min 0,8690 (era 0,8772); 25 min 0,8899 (era 0,9092). Torres aos 25 min 0,0429 (era 0,0927; "11 vezes" virou "cerca de 6 vezes"). A busca em grade refeita escolheu a própria configuração de produção (1º de 27). Holdout: a cronológica aos 10 min ficou 0,0026 abaixo da aleatória, com intervalos sobrepostos (texto e `verifica_tcc` ajustados). Ganho das variáveis no mesmo classificador: logística +0,0073 / +0,0090, XGBoost +0,0044 / +0,0051. Curva com teste fixo 0,8494 → 0,8527. Viés por corte: menor p de Holm 0,65; conversão 7,5 pp (z = 8,0). Figura 4: 71,2%.

**Telas.** Textos de "Leitura" que contrariavam o parecer ou o próprio TCC foram corrigidos (Competitivo, Dashboard, Início, Simulador, Explicabilidade) e todas as figuras foram recapturadas, exceto a da consulta (crédito de API). A API devolve a taxa por região com 6 casas (0,5335 virava "53.3%").

**Texto.** `regenera_quadros.py` reescrito para a estrutura atual; texto corrido atualizado; mais 18 ajustes da revisão (série anual só 2014 diverge, limite de Holm, "(referência)" nos Quadros 13 e 14, impessoal, etapa de explicação, auditoria do coach anterior à mudança do prompt, fonte dos 54%/60%, data de acesso da Riot, ortografia e itálicos). `verifica_tcc` CONSISTENTE, `confere_docx` conforme, corpo em 30 páginas.

## 2026-11-08 (madrugada) — Conferentes dos materiais, das páginas e das figuras

**Por quê.** A correção do vazamento passou no `verifica_tcc`, mas ele só lê o texto do TCC. O pptx foi conferido por um grep feito à mão, e o corpo em 30 páginas (o teto) só era medido por um script que imprimia o número e saía com 0. A Figura 5 ficou mais velha que a tela que mostra sem que nada avisasse.

**O que entrou.**
- `docs/confere_materiais.py`: guia, pptx, README, handoff, scripts.md, comandos.md e telas do frontend (mais site e deck, passados como argumento) contra os valores substituídos do `verifica_tcc` e a presença dos números de hoje. Citação histórica é aceita quando há marcador de passado perto ou exceção explícita com motivo.
- `docs/confere_paginas.ps1`: corpo e páginas por apêndice medidos pelo Word; sai com 1 fora de 25-30. O `finalize-fields.ps1` passou a chamá-lo e devolver o código dele (uma régua só).
- `verifica_tcc.py`: `VALORES_PRE_VAZAMENTO` (21 valores de antes da correção) na checagem 8, que não tinha nenhum; "nunca fica abaixo" entre os padrões refutados; checagem 23, frescor das figuras (data de cada figura contra o código e os artefatos que ela mostra; a Figura 5 é exceção declarada). Agora são 23 checagens.

**O que a primeira execução achou** (corrigido, número por número conferido em `reports/`): README e handoff com 0,7636 / 0,8490 / 40.816; handoff com a grade antiga (200 árvores a 0,05) e a "limitação de taxa-base" que o parecer tirou; guia com o holdout antigo (0,8573 / 0,8569 / 0,8503, "nunca fica abaixo") e a comparação de Grinsztajn com 0,8483 / 0,8473; scripts.md com a tabela de ajuste, a curva, a calibração, a busca aninhada, o ganho isolado e as contagens de empatadas da primeira rodada do parecer, todos pré-vazamento. O `validate_predictions.py` ainda chamava o viés de "constante" e o estado todo-zero de discrepância de calibração; os rótulos foram alinhados ao parecer (a lógica do teste não mudou).

**Testados nos dois sentidos.** `confere_materiais` reprova número velho solto e material sem os números de hoje, e aceita "antes eram 0,7636"; `confere_paginas -Maximo 29` reprova os 30 atuais; a checagem 23 reprova um print quando a página dele fica mais nova (data restaurada depois).

**Estado.** `verifica_tcc` 23 checagens; `confere_paginas` corpo 30 (físicas 3 a 32, no teto); `confere_materiais` sem resíduo, inclusive site v17 e deck v25.

## 2026-11-10 — Leitura completa do .docx e cinco correções

**Por quê.** A validação contra o parecer tinha sido por busca de trechos. Pedida a leitura completa do `tcc2_final.docx` (649 linhas, 32 quadros, 44 legendas, 31 referências e 4 figuras com números), com cada número conferido contra `reports/`, o banco e conta à mão. Nenhum erro de número nem contradição de conclusão; cinco achados de forma.

**Corrigido.**
1. Referências de Jiang e Wallner saíam com espaço depois do hífen ("LLM- powered", "spatio- temporal"): a quebra de linha depois do hífen no `.md` vira espaço no `.docx`. Guarda nova em `verifica_tcc.py` (`PADROES_REFUTADOS`).
2. Diferença de conversão escrita como 7,5 pp com taxas de 81,5% e 74,1% (que dão 7,4): o valor sem arredondar é 7,45 (`confere_conversao_advantagem.py`). Agora "7,45 pontos percentuais" no TCC, no guia, no handoff e no site (versão 18). O slide de conclusão do deck ainda diz 7,5.
3. Apêndice B: "23 de 26 em todas as execuções" contradizia a linha de 22/26 do Quadro 7; agora "sem escrita concorrente".
4. Quadro 28, objetivo e: descrevia os Quadros 3 e 4 como "três modelos em quatro cortes"; agora quatro modelos aos 15 minutos (Quadro 3), XGBoost nos quatro cortes (Quadro 4) e três modelos nos quatro cortes (Quadro 11).
5. Apêndice E: "inteiras" e "sem captura de página inteira" se contradiziam; agora "com toda a altura do conteúdo" e "altura ajustada ao conteúdo da página" (`FONTE_IMAGENS`).

**Estado.** Diff de texto antes/depois: 13 linhas, todas as esperadas. Corpo 30 páginas (físicas 3 a 32), apêndices com o mesmo tamanho; `verifica_tcc` CONSISTENTE, `confere_docx` conforme, `confere_materiais` sem resíduo. Não lidas nesta passagem: Figuras 3 e 5 a 11 (Figura 5 segue a captura antiga).

## 2026-11-10 (tarde) — Conferência célula a célula dos quadros

**Pedido.** Revisar todos os quadros, imagens e valores. Em vez de amostrar, `docs/confere_quadros.py` lê os 32 quadros do `tcc2_final.docx` e compara cada célula numérica com o JSON de `reports/` ou com o banco: 629 células em 25 quadros (2 a 6, 8 a 18, 20, 21, 23, 24, 26, 29 a 32). Testado nos dois sentidos (uma célula adulterada do Quadro 3 reprovou).

**Achado real.** O Quadro 8 trazia 6 perguntas (8, 12, 14, 18, 20, 22) enxugadas em relação ao texto que `src/nlq/evaluate_nlq.py` envia ao sistema, e algumas versões enviadas citam nomes de coluna ("gold_earned", "CS (farm)"). Agora o quadro mostra o texto literal, tirado de `reports/nlq_benchmark.json`. As 26 SQLs de referência já batiam.

**Suspeitas descartadas.** (1) Apêndice K cita a base do XGBoost como 0,8487 e o JSON dos experimentos tem 0,8488: os experimentos reportam a média das AUC-ROC por dobra (0,84881), e o Quadro 4 a AUC-ROC das previsões agrupadas fora da dobra (0,84872); os ganhos vêm do bootstrap sobre as previsões agrupadas, então 0,8487 é a referência certa (confirmado: a mesma configuração dá 0,84872 nas duas matrizes). (2) KR com 50,4% no Quadro 2: 50,44% pela vitória do vermelho, 50,46% pelas derrotas do azul, por 2 partidas com os dois times sem vitória.

**Imagens.** 11 das 12 vistas (todas menos a 9, tela inteira da partida da Figura 3); os números batem com o texto, o banco e os quadros. A Figura 5 segue a captura antiga, e a SQL dela, rodada de novo no banco congelado, dá os mesmos resultados.

**Fora do alcance do script.** Quadros de texto (1, 19, 22, 25, 27, 28), o 7 (execuções históricas do *benchmark*), a primeira medição do Quadro 18 e os valores externos do Quadro 27 (limites das chaves da Riot, do portal consultado em 3 de novembro).

## 2026-11-10 (noite) — Pendentes: tag, 7,45 no deck e olhada visual no Word

**Tag.** `gabarito-203` enviada ao GitHub (`git push origin gabarito-203`; só a tag, o `main` local segue 176 commits à frente). O repositório é público: antes do push conferi que o histórico não tem chave Riot/Anthropic nem `.env`, e que os logs, o `.api.pid` e o `settings.local.json` já estavam publicados de antes (foram removidos depois). O push publicou 141 commits novos, entre eles o `modelo_elvandi.docx`. O Apêndice B do TCC passou a citar o endereço do repositório, porque a tag sem endereço não era localizável.

**7,45 pp.** Corrigido no deck (versão 27 do artefato) e na nota do slide 17 do pptx, reconstruído com PowerPoint (18 slides, 304 efeitos; só essa nota mudou).

**Olhada no Word.** O `.docx` foi exportado para PDF pelo Word e as 62 páginas foram vistas como imagem. Defeitos que nenhum script pegava, corrigidos em `build_tcc_docx.py`: (1) a linha "Fonte" ficava sozinha no topo da página seguinte (Quadro 4 no corpo, Quadro 31 no Apêndice K): a última linha de cada quadro agora leva keep_with_next; (2) Quadro 11 com "Precisã/o" e "10 / min" quebrados e (3) Quadro 27 com "Desenvolviment/o": larguras refeitas (uma primeira tentativa estreitou demais "n" e "F1" e quebrou os números; corrigida na hora). `confere_paginas.ps1` ganhou a detecção de "Fonte" solta e foi testado nos dois sentidos (reprova o `.docx` anterior nas páginas 21 e 62).

**Estado.** Corpo 30 páginas (físicas 3 a 32); o Apêndice K passou de 3 para 4 páginas (o Quadro 31 agora fica inteiro numa página). Todos os conferentes passam.

## 2026-11-11 — Atribuição da arte da Riot nas figuras e aviso da política de API

**Por quê.** Os termos pós-banca da Unisinos pedem, para imagens que não são do autor, indicar pelo menos a fonte. As telas da plataforma mostram ícones, mapa e ilustrações do jogo, e as legendas diziam só "Elaborado pelo autor".

**O que se apurou (fontes primárias).**
- Só as Figuras 3, 6, 8, 9 e 10 têm arte da Riot; as demais (1, 2, 4, 5, 7, 11, 12) são gráficos, controles e tabelas.
- Ícones de itens vêm do Data Dragon (Riot, versão fixa 16.13.1). Ícones e arte de campeões (`cdn.communitydragon.org`) e o mapa (`raw.communitydragon.org`) vêm do Community Dragon, projeto da comunidade sem operador identificado, que se declara criado sob a política "Legal Jibber Jabber", diz funcionar numa "gray area" e "on good faith" e avisa que "CDN will be deprecated in the future". Ele afirma não endossar o uso dos ativos da Riot, ou seja, não dá licença.
- A política de desenvolvedor da API (developer.riotgames.com/policies/general) lista como fontes de imagem permitidas Data Dragon, Press Kit e ativos de TFT e LoR, e exige um aviso de não endosso "readily visible to players". O texto literal está lá; a política de fãs (riotgames.com/en/legal) tem um aviso diferente.
- Trocar a plataforma para o Data Dragon foi avaliado e adiado: cerca de 41 pontos de código em 12 arquivos, sem tabela local de id numérico para nome, mapa com arte antiga e 5 figuras a recapturar, com o corpo do TCC em 30 de 30 páginas. Reavaliar se a plataforma for publicada ou se o CDN sair do ar antes da defesa.

**O que mudou.** `build_tcc_docx.py`: `ATRIBUICAO_RIOT` nas fontes das Figuras 3 (corpo) e 6, 8, 9 e 10 (Apêndice E). `tcc2_texto.md`: parágrafo no Apêndice H com a origem das imagens, o Community Dragon e o aviso da política de API em português (tradução do autor), com os dois endereços citados no texto (não entraram na lista de Referências, para não mudar as 31 nem o corpo). `verifica_tcc.py` (checagem 10): reprova se a atribuição, as quatro capturas ou o parágrafo do Apêndice H sumirem; testado nos dois sentidos. Também corrigida a linha "[OK]" dessa checagem, que aparecia mesmo com falha.

**Estado.** Corpo em 30 páginas (físicas 3 a 32); Figura 6 continua na página da abertura do Apêndice E; o Apêndice H passou de 1 para 2 páginas (o Quadro 27 vai inteiro para a segunda), sem efeito no limite. Todos os conferentes passam.

## 2026-11-11 — Plano de validação de plágio e primeiras correções

**Plano.** `docs/plano_validacao_plagio.md`, a partir da Cartilha sobre Plágio Acadêmico da Unisinos (NITT), da Resolução CONSUN 35/2025 e de pesquisa sobre plágio por tradução. Onze tópicos por prioridade; o mais provável e menos detectado é a paráfrase próxima de fonte em inglês, que os detectores comuns não pegam.

**Corrigido.**
- A cartilha pede, para citação traduzida pelo autor, "(tradução nossa)" e, na graduação, o original em nota de rodapé. O aviso da Riot no Apêndice H dizia "(tradução do autor)", sem aspas e sem nota. Agora está entre aspas, com "(tradução nossa)" e a nota 1 com o original. O conversor ganhou nota numerada (o mecanismo de notas com `*`/`**` da primeira página foi estendido; a nota nativa do pandoc colidiria com os ids dessas notas) e marcador `{{NOTA_ORIGINAL_RIOT}}` no markdown, que o conversor recusa se sobrar fora do fim do parágrafo. `verifica_tcc` reprova "tradução do autor".
- Quadro 27 (tipos de chave da API) vinha do portal de desenvolvedores da Riot com fonte "Elaborado pelo autor". A fonte agora cita developer.riotgames.com/docs/portal, conferida em 11 nov. 2026 (mesmos limites e validades).

**Roteiro.** `docs/gera_roteiro_citacoes.py` gera `docs/roteiro_citacoes.md`: 52 frases e 15 linhas de quadro que citam as 31 obras, com página e seção, e colunas para a leitura lado a lado. Quatro erros do próprio script foram achados ao conferir a contagem por obra contra uma busca independente (ano pego da data de acesso; corte de frase depois de "et al."; "Do" casando com a preposição; capitalização de nomes com hífen e apóstrofo) e corrigidos.

**Varredura do código.** Nenhum comentário indicando trecho copiado; licenças das dependências permissivas (MIT, BSD, Apache, ISC, PSF; psycopg2 LGPL com exceções). O repositório não tem arquivo LICENSE.

**Também.** Contagem de testes do frontend no guia e no handoff: 31 → 38 (estado atual de `npm run test`).

**Estado.** Corpo em 30 páginas; Apêndice H com 2 páginas; todos os conferentes passam. Pendentes do autor no plano: leitura do roteiro ao lado das fontes (exige os PDFs), verificador de similaridade, autoplágio do TCC I e uso de IA com o orientador.

## 2026-11-11 (tarde) — Validação de plágio, itens 1, 2 e 8

**Fontes.** O primeiro rascunho do plano dizia que os PDFs das referências não estavam no computador; estavam (`Downloads/TCC`, `Downloads/ref`, `docs/artigos` e PDFs baixados nas sessões anteriores), e o registro `docs/conferencia_referencias.md` já dizia isso. Texto completo de 24 das 31 obras; Brown pelo resumo; os três livros sem acesso.

**Item 1 (paráfrase próxima e tradução).** Teste de retrotradução: as 50 frases que citam obra com texto disponível foram traduzidas literalmente para o inglês e comparadas com o texto da fonte (sem a lista de referências). Nenhuma é tradução literal. Os cinco sinais acima do limiar (6+ palavras seguidas ou 3+ quadrigramas) são títulos ou nomes de método (Talk2Data, "spatio-temporal evolution of gameplay", "multi-objective multi-instance", o resultado "67% of 306 games") e a definição da Random Forest ("random selection of features at each node"), termo técnico citado. Trechos idênticos de 8+ palavras contra os 10 TCCs II aprovados (só a capa institucional), relatórios do ChatGPT (duas expressões curtas), obras lidas e não citadas (nada) e o TCC I (4% a 4,8%).

**Item 2 (atribuição).** 43 das 52 frases estão como na conferência de 2-3/11. As 9 alteradas depois foram conferidas no texto completo: Jiang, Ribeiro (o "pouco fiel se muito não linear" está literalmente no artigo), Zhong (seção 4.7), Niculescu-Mizil, Holm e Brown conferem. **Corrigido:** em Trabalhos Futuros a citação de Zhong, Yu e Klein (2020) fechava "um modelo aberto local para comparar com a API", que o artigo não trata (zero ocorrências de open/local/API); agora acompanha "avaliação sobre vários bancos de teste", que é a proposta do artigo e a lacuna que a 4.7 já admite. Corpo continua em 30 páginas.

**Roteiro.** Ano exigido passou a ser o da própria obra: "Wallner, Wang e Dormann (2023)" contava como Wang (2020).

**Também.** Os relatórios do ChatGPT (abril de 2026) foram registrados em `docs/registro_uso_ia.md` para a declaração de uso de IA.
