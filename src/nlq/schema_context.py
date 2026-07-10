"""Descrição do schema usada como contexto para o LLM gerar SQL."""

SCHEMA_DESCRIPTION = """
Banco PostgreSQL com dados de partidas ranqueadas de League of Legends.

Tabelas:

matches(match_id, platform_id, queue_id, game_version, game_creation, game_duration_s)
  -- uma linha por partida; queue_id 420 = ranked solo; duração em segundos

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
- Responda APENAS com uma query SQL (SELECT), sem explicação e sem markdown.
- Sempre inclua LIMIT (máximo 100) quando o resultado puder ter muitas linhas.
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
- Se a pergunta pedir uma única resposta ("qual X tem mais/menos Y"), use
  ORDER BY na direção certa e LIMIT 1 — não retorne todas as linhas do
  agrupamento. Isso vale mesmo quando a resposta usa AVG/GROUP BY (ex.:
  "qual time derruba mais torres em média" é resposta única — LIMIT 1,
  não uma linha por time).
"""
