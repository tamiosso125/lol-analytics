# Planejamento v2 — Bellestraiko (pós-roadmap do TCC)

Plano para os 4 objetivos definidos pelo usuário em 2026-07-04, na
ordem de execução sugerida. O roadmap original de 6 etapas do TCC está
concluído (ver `docs/diario_execucao.md`); este documento organiza a
próxima fase. Princípios que valem para tudo aqui: honestidade
estatística primeiro (amostra pequena avisada, heurística ≠ ML), um
passo por vez, e priorizar o que fortalece o texto do TCC antes do que
é só produto.

**Validação externa que chegou junto com este plano**: o próprio
Oracle's Elixir publica uma "Early-Game Win Probability Calculator"
(split + lado do mapa + diferença de ouro aos 15:00 + diferença de
dragões elementais → probabilidade estimada). É exatamente a estrutura
da nossa página de Predição — a fonte dos dados competitivos pratica a
mesma metodologia que implementamos a partir de Hodge et al. (2021).
Além de validar, ela sugere dois enriquecimentos concretos anotados no
Passo 1: lado do mapa como entrada explícita e TIPOS de dragão como
feature (hoje usamos só o agregado `dragon_diff`).

---

## Passo 1 — Competitivo em tudo

**Objetivo:** o dataset pro (13 anos carregados, 2014-2026) deixa de
ser uma página isolada e vira uma dimensão de toda a plataforma.

**Já temos:** `pro_games`/`pro_players` no Postgres, página
`/competitivo` com viés de lado invertido + conversão de ouro + meta
pro × solo queue, match de nomes OE↔Riot resolvido.

**Entregas, em ordem:**
1. **Seletor de ano/split na página Competitivo** — com 13 anos, a
   evolução do meta e do viés de lado ao longo do tempo vira análise
   (o viés azul do pro sempre existiu? cresceu?). Barato: os endpoints
   ganham um param `year`.
2. **NLQ conhece o competitivo** — `pro_games`/`pro_players` no
   `schema_context` + `ALLOWED_TABLES`; adicionar 3-5 perguntas pro ao
   benchmark e RE-RODAR `evaluate_nlq` (regra da casa — já regrediu
   silenciosamente duas vezes).
3. **Seção "no competitivo" no detalhe do campeão** — presença, WR e
   ligas onde é jogado, ao lado das stats de solo queue que já existem.
4. **Modelo de predição PRO aos 15 min** (experimento com valor de
   tese) — treinar o mesmo XGBoost com `gold/xp/cs diff at 15` das
   ~100k partidas pro históricas e comparar a AUC com o modelo de solo
   queue: o jogo profissional é mais previsível a partir do estado?
   (a conversão maior de vantagem sugere que sim). Publicar como
   comparação, não substituir o modelo atual.
5. **Tipos de dragão como feature** (ideia da calculadora do OE) — os
   `ELITE_MONSTER_KILL` das nossas timelines têm o subtipo do dragão;
   testar `infernal_diff`/`mountain_diff`/... no lugar do `dragon_diff`
   agregado. Registrar o resultado mesmo se for nulo (a série de
   experimentos negativos também é material de tese).

**Riscos/cuidados:** sample size por lane no pro é fino para matchups
(6k jogos/ano); não prometer matchup pro no Montar Partida ainda.
Fearless draft (2025+) muda a semântica de picks entre jogos da série.

**Esforço:** baixo por entrega; o modelo pro (item 4) é médio.

---

## Passo 2 — Perfis de jogadores (solo queue + pro) e jogadores no Montar Partida

**Objetivo:** pessoas, não só campeões: perfil clicável de cada
jogador e o Montar Partida aceitando "quem joga", não só "o quê".

**Já temos:** `players` (723+ com game_name/tag preenchidos via
account-v1, crescendo com a coleta), `participants` liga
jogador↔partida↔campeão, `pro_players` tem nome/time/campeão por jogo.
O card "melhor jogador" da Home já aponta a direção.

**Entregas, em ordem:**
1. **Página de perfil solo queue** (`/jogadores/:puuid`) — WR geral,
   partidas, posição principal, pool de campeões (games/WR por
   campeão), últimas partidas (linkando para a análise), forma recente.
   Endpoint `GET /stats/player/{puuid}`. Busca por Riot ID na Home.
2. **Perfil pro** (`/competitivo/jogadores/:nome`) — ligas/times por
   ano, pool de campeões, WR. Tudo já está em `pro_players`.
3. **Jogadores no Montar Partida** — slot opcional de jogador ao lado
   do campeão. O ajuste na estimativa usa o WR do jogador NAQUELE
   campeão com **shrinkage para a taxa do campeão** (encolher a média
   observada proporcionalmente ao n — resolve de vez o item pendente de
   correção de amostra pequena: um jogador 5/5 de Ahri não pode pesar
   como 80% cravado). Mostrar o n e o valor encolhido na UI.
4. **Ligação solo queue ↔ pro** (quando possível) — jogadores pro
   brasileiros aparecem no nosso solo queue Challenger; match por Riot
   ID quando existir. Não forçar: sem match confiável, não liga.

**Riscos/cuidados:** privacidade não é problema (dados públicos da
Riot), mas amostras por jogador-campeão são PEQUENAS — o shrinkage é
obrigatório, não opcional. PUUIDs são estáveis, mas Riot IDs mudam.

**Esforço:** médio. O item 3 é o mais delicado (estatística + UI).

---

## Passo 3 — Mais regiões e elos

**Objetivo:** sair de "BR Challenger/GM" para um recorte multi-região
e multi-elo — generaliza os achados (o viés vermelho é do BR ou do
solo queue de elo alto em geral? — pergunta de tese forte).

**Já temos:** o schema JÁ suporta (players.platform,
matches.platform_id); `.env` tem RIOT_PLATFORM/RIOT_REGION; a coleta é
retomável.

**Entregas, em ordem:**
1. **Pedir a Personal API Key da Riot AGORA** (developer.riotgames.com
   → Register Product). É o desbloqueio real: sem expiração diária e
   limites maiores. A chave de dev (100 req/2min, expira em 24h) não
   escala para multi-região. *Fazer o pedido primeiro porque a
   aprovação leva dias — o resto do passo pode esperar.*
2. **Parametrizar a coleta** — `seed_players`/`collect_matches` aceitam
   `--platform kr euw1 na1` e `--tier CHALLENGER GRANDMASTER MASTER`;
   mapa platform→routing regional (br1/na1→americas, kr/jp1→asia,
   euw1/eune1→europe). O rate limit é por região de roteamento, então
   coletas de regiões diferentes podem intercalar.
3. **Dimensão região/elo nas análises** — filtro de contexto nas
   páginas de estatística (Campeões, Dashboard) e o corte por região
   nos endpoints. Começar simples: um seletor global "Região/Elo" que
   os endpoints já sabem filtrar (WHERE platform_id = ...).
4. **A análise de tese: viés de lado por região** — replicar o achado
   BR (vermelho 56%) em KR/EUW/NA. Se o viés for consistente, é um
   achado sobre solo queue de elo alto; se for só BR, é um achado
   regional. Qualquer resultado é publicável no texto.

**Riscos/cuidados:** o gargalo é TEMPO de coleta, não código. Com a
chave pessoal, ~10k partidas/região é factível em sessões; sem ela,
inviável. Features/modelos por região exigem rerodar build_features/
export_model com o corte certo — decidir se o modelo é global ou por
região (começar global, segmentar se a AUC divergir).

**Esforço:** código baixo; coleta é o custo real (dias, em background).

---

## Passo 4 — Análise em tempo real

**Objetivo:** a meta de longo prazo registrada desde o início: win
probability de partidas AO VIVO.

**Já temos:** `/predict` aceita estado arbitrário por fase (nunca foi
acoplado ao CSV — decisão antiga pensando nisso);
`features_from_timeline` processa payload avulso; e a API do
lolesports (esports-api.lolesports.com, testada em 2026-07-04)
responde com calendário e tem feed de livestats (~frames de 10s) dos
jogos transmitidos.

**Entregas, em ordem (do menor risco para o maior):**
1. **MVP "replay ao vivo" (zero dependência externa)** — página que
   REPRODUZ uma partida já coletada como se fosse ao vivo: a curva de
   probabilidade avança minuto a minuto com play/pause/velocidade.
   Valida toda a arquitetura de streaming de UI (estado incremental,
   atualização suave) sem depender de nenhuma API instável. Também é
   ótima para a BANCA: demonstração ao vivo sem depender de haver jogo
   acontecendo na hora.
2. **Pro ao vivo via feed do lolesports** — poller no backend
   (calendário → jogos ao vivo → window/details a cada ~10s), traduz
   os frames para as nossas features e alimenta o modelo pro (Passo 1
   item 4); página "Ao vivo" com a curva subindo em tempo real.
   Risco: API não documentada, sem garantia — isolar num módulo que
   falha graciosamente.
3. **Minha partida ao vivo (companion local)** — a Live Client Data
   API da Riot (localhost:2999, só funciona na máquina que está
   jogando) dá eventos (abates/torres/dragões) e dados por jogador,
   mas ouro exato só do próprio jogador → exigiria um modelo reduzido
   (features parciais) ou aproximação de ouro via itens+CS. Script
   companion local que posta o estado no backend. Deixar por último:
   mais fricção, feature-set diferente.

**Riscos/cuidados:** APIs de terceiros sem SLA (lolesports) e
particularidades do cliente (Live Client). O MVP do item 1 garante que
o produto "tempo real" existe e é demonstrável mesmo se 2 e 3
emperrarem. Latência/polling: começar com polling simples de 10s
(SSE/WebSocket só se precisar).

**Esforço:** item 1 baixo-médio; item 2 médio-alto (integração
externa); item 3 alto.

---

## Ordem de execução sugerida

| Sprint | Conteúdo | Racional |
|---|---|---|
| 0 (imediato) | Passo 3.1: pedir a Personal API Key | Aprovação demora; destrava o resto |
| 1 | Passo 1 (itens 1-3): ano/split, NLQ pro, campeão no pro | Barato, alto valor de tese, dados já no banco |
| 2 | Passo 1 (itens 4-5): modelo pro + tipos de dragão | Experimentos com resultado publicável |
| 3 | Passo 2 (itens 1-2): perfis de jogador | Base para o resto do passo 2 |
| 4 | Passo 2 (item 3): jogadores no Montar Partida + shrinkage | Fecha pendência estatística antiga |
| 5 | Passo 3 (itens 2-4): coleta multi-região + análise por região | Roda em background durante os sprints seguintes |
| 6 | Passo 4 (item 1): MVP replay ao vivo | Demonstrável para a banca |
| 7+ | Passo 4 (itens 2-3): pro ao vivo, companion | Pós-TCC se o prazo apertar |

**Para o texto do TCC**, o corte natural: sprints 0-4 entram como
resultados; sprint 5 entra se a coleta der tempo (a análise por região
é um capítulo forte); sprint 6 entra como demonstração; 7+ é
"trabalhos futuros" com a pesquisa de replays/CV já documentada no
diário como fundamento.
