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

## Próximos registros pendentes

- NLQ ainda não conhece as tabelas pro_games/pro_players — adicionar ao
  schema_context (e RE-RODAR o evaluate_nlq, regra da casa) quando
  quisermos perguntas em linguagem natural sobre o competitivo.
- Quando a coleta adicional de solo queue terminar: rerodar
  `load_items`, `build_features`, `export_model` e atualizar as tabelas
  de métricas.
- Team builder — próximos incrementos da visão original: jogadores na
  análise e champion select competitivo (o mapa de calor da partida já
  foi entregue na análise de partidas).
- Sinergias de dupla com correção de amostra (shrinkage/IC) para
  perguntas tipo "Nocturne + Orianna" terem resposta estatística mais
  robusta no NLQ e no /compose.
- Atualizar as tabelas de métricas do texto do TCC com os números do
  retreino de 2026-07-03 (acima).
- Revisar os capítulos do texto do TCC com os resultados registrados
  neste diário — usar o nome novo "Hextech Lab".
- Considerar `monotone_constraints` no XGBoost se a banca cobrar
  monotonicidade formal por fator isolado (ver bateria de validação
  acima) — mudança de modelagem, não prioridade atual.
- Extração de itens (ITEM_PURCHASED/SOLD) — candidato mais promissor
  pra realmente melhorar o modelo (não testado ainda; barão/arauto,
  dispersão de time, tuning por fase e calibração já testados hoje e
  não renderam ganho — ver acima). Mapa de calor de visão
  (WARD_PLACED/KILL) segue como incremento de dados viável separado.
- Competitivo/pro-play: adiado (ver acima); se retomado, opções já
  levantadas em `project_scope_decisions.md`.
