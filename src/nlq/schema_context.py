"""Descrição do schema usada como contexto para o LLM gerar SQL."""

SCHEMA_DESCRIPTION = """
Banco PostgreSQL com dados de partidas ranqueadas de League of Legends.

Tabelas:

matches(match_id, platform_id, queue_id, game_version, game_creation, game_duration_s)
  -- uma linha por partida; queue_id 420 = ranked solo; duração em segundos
  -- game_creation é TIMESTAMPTZ (data e hora da partida), NÃO epoch em
  -- milissegundos: para o ano use EXTRACT(YEAR FROM game_creation) = 2026;
  -- nunca to_timestamp(game_creation / 1000) (dá erro de tipo).

teams(match_id, team_id, win, barons, dragons, heralds, towers, inhibitors)
  -- duas linhas por partida; team_id 100 = time azul, 200 = time vermelho

participants(match_id, puuid, team_id, team_position, champion_id, champion_name,
             kills, deaths, assists, gold_earned, cs_total, vision_score,
             dmg_to_champions, win)
  -- dez linhas por partida; team_position em: TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY
  -- IMPORTANTE: gold_earned, kills, deaths, assists, cs_total, dmg_to_champions
  -- são totais FINAIS da partida (fim de jogo), não um estado em um minuto
  -- específico. Da mesma forma, matches.game_duration_s é a duração TOTAL da
  -- partida, não o instante em que algo aconteceu. NENHUMA tabela aqui tem o
  -- estado da partida em um minuto específico (isso só existe em timelines
  -- brutas, fora deste schema) — nunca use game_duration_s ou qualquer total
  -- final como aproximação de "aos N minutos" ou "no minuto N".

players(puuid, game_name, tag_line, tier, division, league_points, platform, updated_at)
  -- tier armazenado em MAIÚSCULAS, exatamente como a Riot API retorna
  -- (CHALLENGER, GRANDMASTER, MASTER, DIAMOND...); compare com
  -- UPPER(tier) = UPPER('...') para ser robusto a diferenças de caixa.

pro_games(game_id, league, year, split, playoffs, game_date, patch, side,
          team_name, win, game_length_s, kills, deaths, dragons, barons,
          heralds, towers, inhibitors, gold_diff_at15, xp_diff_at15, cs_diff_at15)
  -- partidas PROFISSIONAIS/competitivas (Oracle's Elixir, 2014-2026),
  -- duas linhas por jogo (uma por time). ATENÇÃO: aqui "side" é texto
  -- 'Blue'/'Red' (NÃO team_id 100/200 — isso é só nas tabelas de solo
  -- queue). league é a sigla da liga ('LCK', 'LPL', 'LEC'...).
  -- game_date dá a ORDEM CRONOLÓGICA dos jogos (use ORDER BY game_date, game_id).
  -- gold_diff_at15 é na perspectiva DAQUELA linha/time. Jogos =
  -- COUNT(DISTINCT game_id). SEMPRE filtre por year quando a pergunta
  -- indicar um ano (sem filtro, 13 anos de metas diferentes se misturam
  -- — se a pergunta não citar ano, use year = 2026, o mais recente).

pro_players(game_id, side, position, player_name, team_name, champion,
            kills, deaths, assists, win)
  -- dez linhas por jogo profissional; position em: top, jng, mid, bot,
  -- sup (minúsculas — padrão diferente do solo queue!). champion é o
  -- NOME DE EXIBIÇÃO com espaços ('Xin Zhao', 'Renata Glasc' — não o
  -- nome interno de participants). NÃO tem coluna year: para filtrar
  -- por ano, junte com pro_games POR (game_id, side) — junte pelas
  -- DUAS colunas, senão cada linha duplica. Exemplo — campeões mais
  -- jogados no competitivo em 2026:
  -- SELECT pp.champion, COUNT(*) AS jogos
  -- FROM pro_players pp
  -- JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
  -- WHERE pg.year = 2026
  -- GROUP BY pp.champion ORDER BY jogos DESC LIMIT 5;

bans(match_id, team_id, pick_turn, champion_id)
  -- banimentos do champion select (até 5 por time por partida); NÃO tem
  -- champion_name. NUNCA junte "bans" direto com "participants" por
  -- champion_id (participants tem ~10 linhas por partida — o join cria
  -- uma explosão cartesiana e a query estoura o timeout do banco).
  -- bans não tem data: para filtrar por ano junte com matches por match_id e
  -- use EXTRACT(YEAR FROM matches.game_creation).
  -- Para obter o nome, junte com uma subquery DEDUPLICADA por
  -- champion_id (join 1-para-1, não 1-para-muitos). Exemplo — os 5
  -- campeões mais banidos e a taxa de banimento de cada um:
  -- SELECT c.champion_name, COUNT(DISTINCT b.match_id) AS bans,
  --        COUNT(DISTINCT b.match_id)::float / (SELECT COUNT(*) FROM matches) AS ban_rate
  -- FROM bans b
  -- JOIN (SELECT DISTINCT champion_id, champion_name FROM participants) c
  --   ON c.champion_id = b.champion_id
  -- GROUP BY c.champion_name ORDER BY bans DESC LIMIT 5;

item_events(match_id, puuid, ts_ms, item_id, action)
  -- compras/vendas EFETIVAS de item por jogador (ITEM_UNDO já desfeito
  -- no ETL — reflete o que o jogador manteve, não cada clique na
  -- loja). NÃO tem champion_name nem win — junte com participants por
  -- (match_id, puuid). NÃO tem nome do item — item_id é só número;
  -- pra nome, JUNTE com items (abaixo), NUNCA responda com o nome de
  -- um item de memória (você pode errar o item — já aconteceu). action
  -- é 'BUY', 'SELL' ou 'DESTROY' (componente consumido numa receita —
  -- o jogador COMPROU sim, só não ficou com aquele item específico no
  -- fim; não é "não comprou"). Pra "quais itens o campeão X mais
  -- constrói" conte pela PRIMEIRA compra de cada item por partida
  -- (MIN(ts_ms), sempre filtrando action='BUY') — sem isso, recompra
  -- do mesmo item após vender conta como dois jogos por engano.

items(item_id, name, total_gold, purchasable, map_11)
  -- catálogo (Data Dragon) — nome, custo e se é válido no mapa 11
  -- (Summoner's Rift; sem esse filtro, item só de ARAM/outros modos
  -- pode aparecer no meio do resultado). Pra pergunta de BUILD ("quais
  -- itens X mais constrói"), SEMPRE filtre também total_gold >= 1300 —
  -- sem isso o resultado fica dominado por poção, ward, bota básica e
  -- componente barato (ex.: Espada Longa, Cristal de Rubi), que tecnicamente
  -- são "comprados" mas não são o que a pergunta quer dizer com "build".
  -- Exemplo — os 5 itens de build mais construídos pela Camille, com win
  -- rate real:
  -- WITH champ AS (
  --   SELECT match_id, puuid, win FROM participants WHERE champion_name = 'Camille'
  -- ), first_buys AS (
  --   SELECT ie.match_id, ie.puuid, ie.item_id, MIN(ie.ts_ms) AS ts_ms
  --   FROM item_events ie
  --   JOIN champ c ON c.match_id = ie.match_id AND c.puuid = ie.puuid
  --   WHERE ie.action = 'BUY'
  --   GROUP BY ie.match_id, ie.puuid, ie.item_id
  -- )
  -- SELECT i.name, COUNT(*) AS jogos, AVG(c.win::int) AS win_rate
  -- FROM first_buys fb
  -- JOIN champ c ON c.match_id = fb.match_id AND c.puuid = fb.puuid
  -- JOIN items i ON i.item_id = fb.item_id AND i.map_11 AND i.total_gold >= 1300
  -- GROUP BY i.name
  -- HAVING COUNT(*) >= 20
  -- ORDER BY jogos DESC LIMIT 5;

Regras:
- Responda APENAS com uma query SQL (SELECT), sem explicação e sem markdown. Escreva
  UMA consulta final: nada de comentários, "Wait", correção ou segunda tentativa.
- Sempre inclua LIMIT (máximo 100) quando o resultado puder ter muitas linhas. Se a
  pergunta pede TODOS os que atendem a um critério ("quais campeões tiveram mais de N
  partidas?", sem um número de itens), use LIMIT 500: cortar em 100 devolve lista incompleta.
- Win rate = AVG(win::int) ou AVG(CASE WHEN win THEN 1.0 ELSE 0 END), sempre
  como fração entre 0 e 1 — nunca multiplique por 100 nem arredonde para
  formato de porcentagem.
- Regra obrigatória para taxas (win rate ou qualquer proporção) de UM
  SUBGRUPO específico (ex.: "o time vermelho") dentro de uma consulta
  que agrupa por outra coisa (ex.: por duração da partida) SEM colocar
  esse subgrupo no GROUP BY: filtre esse subgrupo com WHERE, e só
  DEPOIS agregue com AVG(win::int) simples — NUNCA com um `CASE WHEN
  <condição do subgrupo> THEN ... ELSE 0 END` dentro do AVG rodando
  sobre linhas de fora do subgrupo, porque o denominador do AVG conta
  essas linhas de fora e dilui a taxa (costuma sair pela metade do
  valor real). Exemplo — win rate do time vermelho por faixa de
  duração da partida:
  SELECT CASE WHEN m.game_duration_s < 1500 THEN 'curta' ELSE 'longa' END AS faixa,
         AVG(t.win::int) AS win_rate_vermelho, AVG(t.dragons) AS media_dragoes
  FROM matches m JOIN teams t ON t.match_id = m.match_id
  WHERE t.team_id = 200
  GROUP BY faixa;
  Se a pergunta pedir os dois lados lado a lado (vermelho E azul),
  agrupe por team_id também (GROUP BY faixa, team_id) em vez de
  filtrar — mas sempre sem CASE dentro do AVG nesses casos.
- Selecione APENAS as colunas necessárias para responder à pergunta. Não
  adicione colunas extras (contagem de linhas, métricas auxiliares, rótulos
  amigáveis) a menos que a pergunta peça explicitamente por elas.
- Para team_id, retorne o valor bruto (100 ou 200) em vez de rótulos como
  "Azul"/"Vermelho", a menos que a pergunta peça um nome amigável.
- Responda SEMPRE com uma única query SELECT válida — mesmo se a mensagem
  for uma correção, esclarecimento ou não parecer uma pergunta direta.
  Nunca responda com texto livre fora de uma query.
- Se a pergunta pedir algo que não existe neste schema (ex.: estado da
  partida em um minuto específico, dados de timeline, qualquer coisa que
  exigiria um "instante" em vez de um total final — ver aviso acima em
  participants), NÃO invente uma aproximação. Responda com:
  SELECT 'não é possível responder: <motivo curto e específico>' AS aviso;
- Perguntas sobre COMPOSIÇÕES/matchups de times SÃO respondíveis:
  "campeão A e B no mesmo time contra C e D" filtra partidas com EXISTS
  por campeão, amarrando os do mesmo time ao MESMO team_id e os inimigos
  ao team_id oposto. APENAS nesse tipo de pergunta de composição
  específica, inclua também COUNT(*) de partidas no resultado (essas
  combinações têm amostras pequenas). Em qualquer OUTRA pergunta
  (rankings, win rate por campeão/posição, agregações simples), a regra
  de não adicionar colunas extras continua valendo: NÃO acrescente a
  contagem se não foi pedida. Exemplo — win rate do time com Senna+Brand
  contra Vayne+Lulu:
  SELECT AVG(p.win::int) AS win_rate, COUNT(DISTINCT p.match_id) AS partidas
  FROM participants p
  WHERE p.champion_name = 'Senna'
    AND EXISTS (SELECT 1 FROM participants a WHERE a.match_id = p.match_id
                AND a.team_id = p.team_id AND a.champion_name = 'Brand')
    AND EXISTS (SELECT 1 FROM participants i WHERE i.match_id = p.match_id
                AND i.team_id != p.team_id AND i.champion_name = 'Vayne')
    AND EXISTS (SELECT 1 FROM participants i WHERE i.match_id = p.match_id
                AND i.team_id != p.team_id AND i.champion_name = 'Lulu');
- SINERGIA DE DUPLA — só quando a pergunta cita DOIS CAMPEÕES pelo nome
  e pergunta se combinam bem ("X e Y têm sinergia?", "vale jogar X com
  Y?"; NÃO se aplica a ranking/média por time ou posição, tipo "qual
  time derruba mais torres" — isso continua seguindo a regra de LIMIT 1
  abaixo normalmente): além de jogos e win rate bruto da dupla (WHERE/
  EXISTS do exemplo de composição acima), inclua a expectativa sem
  sinergia (média dos win rates solo, subquery `(SELECT AVG(win::int)
  FROM participants WHERE champion_name = 'X')` para cada) e um valor
  ajustado por shrinkage `(jogos*bruto + 20*expectativa) / (jogos+20)`.
- SOLO QUEUE × COMPETITIVO quando a pergunta não disser qual: "equipe",
  "jogador" (pelo nome), "liga", "temporada" e "patch" indicam o COMPETITIVO
  (pro_games/pro_players, com team_name e player_name); "time azul/vermelho",
  "campeão" e "posição" sem essas pistas indicam o solo queue (teams/
  participants). No solo queue NÃO existe nome de equipe (só team_id 100/200),
  e players.game_name é NULL para quase todos os jogadores: não monte ranking
  de jogadores do solo queue por nome.
- NÃO EXISTE no schema quem fez algo PRIMEIRO (primeiro dragão, primeiro barão,
  primeira torre, primeiro abate): teams e pro_games só têm a contagem total.
  Nunca use "dragons > 0" ou "towers > 0" como aproximação; responda com o
  aviso de "não é possível responder".
- Ranking ou extremo ("maior", "menor", "melhor", "pior") de uma MÉDIA ou TAXA
  (win rate, média de kills, mortes, torres, duração...) de campeão, equipe, jogador
  ou liga, sem limiar citado na pergunta: exija amostra mínima com HAVING COUNT(*)
  >= 20 no solo queue e HAVING COUNT(*) >= 10 no competitivo (uma liga: >= 30 jogos,
  COUNT(DISTINCT game_id)); um grupo com 1 jogo e 100% de vitória, ou com 4 jogos e
  média alta, não é resposta. Não vale para CONTAGENS ("mais jogados"). Se a pergunta citar um limiar ("com pelo menos
  N partidas"), use o dela. Em AMBOS os casos o limiar vai SÓ no HAVING: a
  contagem NÃO vira coluna do resultado (nem COUNT(*) AS partidas, nem jogos),
  porque a pergunta não a pediu.
- ORDENAÇÃO E NULOS: no PostgreSQL, ORDER BY ... DESC põe os valores NULOS
  PRIMEIRO, então um ranking pode ser liderado por um grupo sem dado. Em todo
  ranking use ORDER BY métrica DESC NULLS LAST e, quando a métrica pode ser
  nula (ex.: gold_diff_at15, xp_diff_at15 e cs_diff_at15 de pro_games, que são
  nulos em parte dos jogos; divisão com NULLIF), filtre métrica IS NOT NULL.
- "O X DE CADA Y" (o campeão mais escolhido em cada liga, o melhor jogador de
  cada equipe, os N melhores de cada grupo): uma linha por grupo, NÃO LIMIT.
  Use ROW_NUMBER() OVER (PARTITION BY grupo ORDER BY métrica DESC NULLS LAST)
  numa subconsulta e filtre rn = 1 (ou rn <= N).
- O QUE ESTE SCHEMA NÃO TEM — responda com o aviso de "não é possível
  responder", sem aproximar nem trocar por uma métrica parecida:
    * solo queue: pentakill ou qualquer sequência de abates (kills >= 5 não é
      pentakill), quem fez algo primeiro (primeiro sangue, dragão, barão, torre
      ou arauto), estado da partida em um minuto específico, nome de jogador
      (players.game_name é quase sempre NULL);
    * competitivo: ouro total, CS total, dano, visão e banimentos. pro_games só
      tem gold_diff_at15, xp_diff_at15 e cs_diff_at15 (DIFERENÇAS aos 15
      minutos), e pro_players só tem kills, deaths e assists; também não há
      quem fez algo primeiro.
  Diferença de ouro aos 15 minutos não é ouro total, e kills >= 5 não é
  pentakill. Exemplo — "qual equipe tem a maior média de ouro obtido por
  partida?" no competitivo:
  SELECT 'não é possível responder: pro_games só tem a DIFERENÇA de ouro aos 15 minutos (gold_diff_at15), não o ouro total da equipe' AS aviso;
- COMPETITIVO, EQUIPE E JOGO: pro_games tem UMA linha por equipe em cada jogo, e
  kills, deaths, dragons, barons, heralds, towers e inhibitors são da EQUIPE naquele
  jogo. Para "equipe" use pro_games, NÃO pro_players (cada linha de pro_players é um
  jogador: a média sai por jogador, cerca de 1/5 do valor da equipe). O total das
  duas equipes de um jogo é SUM(coluna) ... GROUP BY game_id; a diferença entre a
  equipe e o adversário vem de uma auto-junção por game_id com side diferente.
  Exemplo — equipe com a maior diferença média de torres sobre o adversário em 2026:
  SELECT a.team_name, AVG(a.towers - b.towers) AS dif
  FROM pro_games a JOIN pro_games b ON b.game_id = a.game_id AND b.side <> a.side
  WHERE a.year = 2026 GROUP BY a.team_name HAVING COUNT(*) >= 10
  ORDER BY dif DESC NULLS LAST LIMIT 1;
- CONTAR JOGOS ou PARTIDAS dá UMA linha: agrupe por jogo numa SUBconsulta e conte
  fora dela; nunca deixe GROUP BY game_id (ou match_id) no nível externo, que devolve
  uma linha por jogo. "Nenhuma equipe teve X" é HAVING MAX(X) = 0 (WHERE X = 0 pega
  também jogos em que só UMA das equipes não teve). Exemplo — jogos com mais de 6
  dragões somando as duas equipes:
  SELECT COUNT(*) AS jogos FROM (
    SELECT game_id FROM pro_games GROUP BY game_id HAVING SUM(dragons) > 6) s;
  No solo queue é igual, com matches/teams e match_id.
- TOTAL × UMA PARTIDA: "o jogador (ou campeão) com a maior quantidade de X em
  [período]", sem "por partida", "média" nem "em uma única partida", é a SOMA de X
  por jogador (GROUP BY, SUM(X)), não as linhas individuais. "Em uma única partida"
  é o MAIOR valor de uma linha.
- SEQUÊNCIAS CONSECUTIVAS (vitórias ou derrotas seguidas): numere os jogos de cada
  equipe em ordem cronológica e subtraia a numeração dentro de cada resultado;
  filtre win/NOT win SÓ DEPOIS de calcular o grupo, porque filtrar antes apaga as
  derrotas que quebram a sequência. Exemplo — maior sequência de vitórias em 2026:
  SELECT team_name, MAX(seq) AS maior_sequencia FROM (
    SELECT team_name, COUNT(*) AS seq FROM (
      SELECT team_name, win,
             ROW_NUMBER() OVER (PARTITION BY team_name ORDER BY game_date, game_id)
           - ROW_NUMBER() OVER (PARTITION BY team_name, win ORDER BY game_date, game_id) AS grp
      FROM pro_games WHERE year = 2026) t
    WHERE win GROUP BY team_name, grp) s
  GROUP BY team_name ORDER BY maior_sequencia DESC LIMIT 1;
  Para derrotas troque WHERE win por WHERE NOT win.
- BANIMENTOS no competitivo NÃO existem. Contar pro_players.champion conta ESCOLHAS
  (picks): nunca rotule isso como "bans" nem responda como se fosse banimento; use o
  aviso de "não é possível responder". Banimentos só existem no solo queue (tabela bans).
- "TEMPORADA", "este ano" e "atual" valem 2026: pro_games.year = 2026 (solo queue:
  EXTRACT(YEAR FROM game_creation) = 2026), mesmo que a pergunta não escreva o ano.
  Sem essas palavras nem um ano escrito, NÃO filtre o ano: vale a base inteira.
- "PRINCIPAIS LIGAS" no competitivo: filtre league IN ('LCK','LPL','LEC','LCP','LTA',
  'LCS','CBLOL'); sem esse filtro entram dezenas de ligas regionais e de acesso.
- ELIMINAÇÕES, ABATES e KILLS são a coluna kills. Assistências só entram em
  "participação nas eliminações" (kills + assists) ou quando a pergunta cita
  assistências; "pelo menos 10 eliminações" é kills >= 10, não kills + assists.
- VENCEDOR × PERDEDOR do mesmo jogo: auto-junção de pro_games por game_id com
  a.win e NOT b.win (ou side diferente). "A equipe com menos eliminações venceu" é
  a.win AND a.kills < b.kills, comparando com o ADVERSÁRIO daquele jogo, nunca com o
  mínimo da tabela inteira. Exemplo — jogos em que o vencedor teve menos kills:
  SELECT COUNT(*) AS jogos FROM pro_games a JOIN pro_games b
    ON b.game_id = a.game_id AND b.side <> a.side
  WHERE a.win AND a.kills < b.kills;
- PORCENTAGEM ou FREQUÊNCIA de jogos (ou equipes) que cumprem uma condição, em tabela
  de DUAS linhas por jogo: AVG(CASE WHEN condição THEN 1.0 ELSE 0 END) por grupo.
  Nunca divida SUM(...) por COUNT(DISTINCT game_id), que dobra o numerador, nem
  divida uma contagem por ela mesma. Condição sobre o TOTAL das duas equipes (ex.:
  mais de 30 kills somando as duas) pede subconsulta por game_id com SUM(kills), e
  só depois a média por liga.
- "AS DUAS EQUIPES tiveram X" ("em quantas partidas as duas conquistaram um Barão"):
  UMA linha, com a contagem FORA da subconsulta: SELECT COUNT(*) FROM (SELECT game_id
  FROM pro_games GROUP BY game_id HAVING MIN(barons) >= 1) s. Nunca devolva uma
  linha por jogo.
- NÃO use subconsulta correlacionada por linha sobre pro_players ou participants
  (estoura o tempo limite de 10 s): pré-agregue em CTE ou subconsulta com GROUP BY
  e faça JOIN.
- DIFERENÇA entre dois lados ou grupos (azul × vermelho, vitória × derrota) de uma
  mesma entidade: UMA linha por entidade com a coluna da diferença, calculada com
  AVG(...) FILTER (WHERE ...) ou duas CTEs com JOIN; não devolva as duas taxas em
  linhas separadas. Se a pergunta pedir "qual" entidade tem a maior diferença, ordene
  por ABS(diferença) e aplique o limiar de amostra mínima.
- JOGADOR no solo queue: agrupe por puuid e devolva o puuid (não recuse só porque
  game_name é NULL). A recusa por falta de nome só vale quando a pergunta exige o nome.
- Se a pergunta pedir uma única resposta ("qual X tem mais/menos Y"), use
  ORDER BY na direção certa e LIMIT 1 — não retorne todas as linhas do
  agrupamento. Isso vale mesmo quando a resposta usa AVG/GROUP BY (ex.:
  "qual time derruba mais torres em média" é resposta única — LIMIT 1,
  não uma linha por time).
"""
