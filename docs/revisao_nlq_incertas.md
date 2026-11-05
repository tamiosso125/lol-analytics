# As 20 respostas do coach de consulta de que não tenho certeza

Gerado em 2026-11-04 a partir da última rodada das 50 perguntas (`independentes_resultado.json`, fora do repositório).
Cada item traz a pergunta, a SQL que o sistema gerou, o resultado e a minha dúvida. Marque a sua opção em **Sua resposta**.


## A. Solo queue ou profissional?

### #3 — Qual lado do mapa apresentou a maior taxa de vitória?

**SQL:** `SELECT side, AVG(win::int) AS win_rate FROM pro_games GROUP BY side ORDER BY win_rate DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['Blue', '0.53197191186693398080']]

**Minha dúvida:** Respondeu o profissional (azul 53,2%, todos os anos). No solo queue o vermelho vence mais. Qual era a intenção?

**Sua resposta:** [ ] solo queue  [ ] profissional  [ ] os dois

### #7 — Qual foi a partida mais longa registrada em 2026?

**SQL:** `SELECT match_id, game_duration_s FROM matches WHERE EXTRACT(YEAR FROM game_creation) = 2026 ORDER BY game_duration_s DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['BR1_3253233939', '3462']]

**Minha dúvida:** Respondeu o solo queue. A pergunta anterior diz "profissionais"; a 7 e a 8 também são do profissional?

**Sua resposta:** [ ] solo queue  [ ] profissional

### #8 — Qual foi a partida mais curta registrada em 2026?

**SQL:** `SELECT match_id, game_duration_s FROM matches WHERE EXTRACT(YEAR FROM game_creation) = 2026 ORDER BY game_duration_s ASC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['BR1_3248552796', '302']]

**Minha dúvida:** Mesma dúvida da 7.

**Sua resposta:** [ ] solo queue  [ ] profissional

### #9 — Quantas partidas terminaram antes dos 25 minutos?

**SQL:** `SELECT COUNT(*) AS partidas FROM matches WHERE game_duration_s < 1500;`

**Resultado (executou, 1 linhas):** [['15944']]

**Minha dúvida:** Respondeu o solo queue (15.944 partidas). Podia ser o profissional.

**Sua resposta:** [ ] solo queue  [ ] profissional

### #10 — Qual equipe apresentou a maior taxa de vitória em partidas com duração superior a 35 minutos?

**SQL:** `SELECT t.team_id, AVG(t.win::int) AS win_rate FROM matches m JOIN teams t ON t.match_id = m.match_id WHERE m.game_duration_s > 2100 GROUP BY t.team_id ORDER BY win_rate DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['200', '0.54041435658009921214']]

**Minha dúvida:** Diz "equipe", que pelo esquema é profissional, mas respondeu o solo queue e devolveu um lado (200), não uma equipe. Provavelmente errada.

**Sua resposta:** [ ] solo queue  [ ] profissional (equipe com nome)

### #15 — Qual campeão teve a maior quantidade de eliminações em uma única partida?

**SQL:** `SELECT champion_name, kills FROM participants ORDER BY kills DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['Rengar', '41']]

**Minha dúvida:** Respondeu o solo queue (Rengar, 41 abates). Podia ser o profissional.

**Sua resposta:** [ ] solo queue  [ ] profissional

### #38 — Qual equipe apresentou a maior média de eliminações por partida?

**SQL:** `SELECT team_id, AVG(p.kills) AS media_kills FROM teams t JOIN participants p ON p.match_id = t.match_id AND p.team_id = t.team_id GROUP BY t.team_id ORDER BY media_kills DESC LIMIT 1;`

**Resultado (erro, None linhas):** []

**Minha dúvida:** Deu erro de coluna ambígua no solo queue. "Equipe" seria o profissional?

**Sua resposta:** [ ] solo queue  [ ] profissional


## B. Ano não citado

### #22 — Quais foram os 10 jogadores com maior KDA médio?

**SQL:** `SELECT pp.player_name, AVG((pp.kills + pp.assists)::float / NULLIF(pp.deaths, 0)) AS kda_medio FROM pro_players pp GROUP BY pp.player_name HAVING COUNT(*) >= 10 ORDER BY kda_medio DESC LIMIT 10;`

**Resultado (executou, 10 linhas):** [['DG kumuo', '9.602678571428571'], ['HKE MaLiCE', '9.225925925925926'], ['Greggers', '8.883333333333333']]

**Minha dúvida:** Sem ano na pergunta: usou todos os anos. O esquema manda usar 2026 quando o ano não é citado. Também é média de razões (ignora partidas com zero morte).

**Sua resposta:** [ ] todos os anos  [ ] 2026

### #32 — Quais foram as 5 equipes que mais conquistaram Barões Nashor?

**SQL:** `SELECT team_name, SUM(barons) AS total_barons FROM pro_games GROUP BY team_name ORDER BY total_barons DESC LIMIT 5;`

**Resultado (executou, 5 linhas):** [['KT Rolster', '884'], ['Bilibili Gaming', '867'], ['Dplus Kia', '860']]

**Minha dúvida:** Sem ano na pergunta: usou todos os anos (o esquema manda 2026).

**Sua resposta:** [ ] todos os anos  [ ] 2026

### #40 — Quais equipes conseguiram vencer partidas mesmo estando com desvantagem de ouro aos 15 minutos?

**SQL:** `SELECT pg.team_name, COUNT(DISTINCT pg.game_id) AS partidas_vencidas FROM pro_games pg WHERE pg.win = true AND pg.gold_diff_at15 < 0 GROUP BY pg.team_name ORDER BY partidas_vencidas DESC LIMIT 100;`

**Resultado (executou, 100 linhas):** [['G2 Esports', '175'], ['Gen.G', '174'], ['KT Rolster', '170']]

**Minha dúvida:** Sem ano na pergunta: usou todos os anos e devolveu 100 equipes.

**Sua resposta:** [ ] todos os anos  [ ] 2026

### #42 — Quais foram as 5 ligas com maior duração média de partida?

**SQL:** `SELECT league, AVG(game_length_s) AS duracao_media FROM pro_games GROUP BY league ORDER BY duracao_media DESC LIMIT 5;`

**Resultado (executou, 5 linhas):** [['OGN', '2341.0380710659898477'], ['EU LCS', '2213.1563706563706564'], ['NA LCS', '2195.2384792626728111']]

**Minha dúvida:** Sem ano na pergunta: usou todos os anos e sem amostra mínima (OGN lidera, liga antiga).

**Sua resposta:** [ ] todos os anos  [ ] 2026  [ ] com mínimo de jogos


## C. Definição da métrica

### #18 — Qual campeão apresentou o maior KDA médio em 2026?

**SQL:** `SELECT champion_name, AVG((kills + assists)::float / NULLIF(deaths, 0)) AS avg_kda FROM participants p JOIN matches m ON m.match_id = p.match_id WHERE EXTRACT(YEAR FROM m.game_creation) = 2026 GROUP BY champion_name HAVING COUNT(*) >= 20 ORDER BY avg_kda DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['Ivern', '6.000249084581662']]

**Minha dúvida:** KDA como média de razões por partida: ignora as partidas com zero morte. A alternativa é (abates + assistências) somados dividido pelas mortes somadas.

**Sua resposta:** [ ] média por partida  [ ] agregado

### #24 — Qual jogador apresentou o maior CS por minuto na posição MIDDLE?

**SQL:** `SELECT p.puuid, p.champion_name, AVG(p.cs_total::float / (m.game_duration_s::float / 60)) AS cs_per_minute FROM participants p JOIN matches m ON m.match_id = p.match_id WHERE p.team_position = 'MIDDLE' GROUP BY p.puuid, p.champion_name HAVING COUNT(*) >= 20 ORDER BY cs_per_minute DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['WjG0iCHJIISeAzTfuhHtLNmP4iF97RPPAyIAX6nO', 'Irelia', '9.945098079086252']]

**Minha dúvida:** Devolve um puuid e um campeão (jogador do solo queue não tem nome legível), com mínimo de 20 jogos no mesmo campeão. Serve?

**Sua resposta:** [ ] serve  [ ] queria o competitivo  [ ] queria por jogador com mínimo geral

### #50 — Qual foi a diferença na média de eliminações por partida entre as principais ligas profissionais em 2026?

**SQL:** `SELECT pg.league, AVG(pg.kills) AS media_eliminacoes FROM pro_games pg WHERE pg.year = 2026 GROUP BY pg.league ORDER BY media_eliminacoes DESC;`

**Resultado (executou, 43 linhas):** [['HC', '20.6262626262626263'], ['HM', '20.4602272727272727'], ['HW', '20.1796116504854369']]

**Minha dúvida:** "Principais ligas" não está definido. Devolveu as médias de 43 ligas, sem calcular nenhuma diferença.

**Sua resposta:** [ ] listar as médias  [ ] calcular a diferença entre as maiores  [ ] recusar


## D. Amostra pequena

### #43 — Qual liga apresentou a maior média de eliminações por partida?

**SQL:** `SELECT league, AVG(kills) AS media_eliminacoes FROM pro_games WHERE year = 2026 GROUP BY league ORDER BY media_eliminacoes DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['HC', '20.6262626262626263']]

**Minha dúvida:** HC lidera com 20,6 abates por jogo. É uma liga com poucos jogos? Falta amostra mínima?

**Sua resposta:** [ ] ok  [ ] exigir mínimo de jogos

### #45 — Qual liga apresentou a maior taxa de vitória do lado azul?

**SQL:** `SELECT pg.league, AVG(CASE WHEN pg.side = 'Blue' THEN pg.win::int ELSE NULL END) AS win_rate_blue FROM pro_games pg WHERE pg.year = 2026 GROUP BY pg.league ORDER BY win_rate_blue DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['MSI', '0.70588235294117647059']]

**Minha dúvida:** MSI lidera com 70,6% do lado azul, mas são só 34 jogos.

**Sua resposta:** [ ] ok  [ ] exigir mínimo de jogos

### #47 — Qual liga apresentou a maior média de dragões conquistados por partida?

**SQL:** `SELECT pg.league, AVG(pg.dragons) AS media_dragoes FROM pro_games pg WHERE pg.year = 2026 GROUP BY pg.league ORDER BY media_dragoes DESC LIMIT 1;`

**Resultado (executou, 1 linhas):** [['AC', '2.5263157894736842']]

**Minha dúvida:** AC lidera com 2,53 dragões por jogo. Pode ter poucos jogos.

**Sua resposta:** [ ] ok  [ ] exigir mínimo de jogos


## E. Recusas possivelmente erradas

### #27 — Qual foi o jogador com maior participação nas eliminações da equipe?

**SQL:** `SELECT 'não é possível responder: o schema não contém dados de quem fez o primeiro abate ou participação em eliminações específicas — apenas totais finais de kills, deaths e assists por partida' AS aviso;`

**Resultado (executou, 1 linhas):** [['não é possível responder: o schema não c']]

**Minha dúvida:** Recusou, citando "primeiro abate", que não é o da pergunta. Participação nas eliminações = (abates + assistências) do jogador / abates do time, que dá para calcular no competitivo.

**Sua resposta:** [ ] recusa certa  [ ] devia responder

### #49 — Quais campeões tiveram o maior aumento na taxa de escolha entre dois patches consecutivos?

**SQL:** `SELECT 'não é possível responder: o schema não contém informações de patch para solo queue (participants), apenas para pro_games' AS aviso;`

**Resultado (executou, 1 linhas):** [['não é possível responder: o schema não c']]

**Minha dúvida:** Recusou dizendo que só o solo queue não tem patch. O competitivo tem patch (pro_games.patch) e a pergunta pode ser respondida lá, embora seja complexa.

**Sua resposta:** [ ] recusa certa  [ ] devia responder


## F. Caso à parte

### #19 — Quais campeões foram utilizados em todas as cinco posições?

**SQL:** `SELECT champion_name FROM participants GROUP BY champion_name HAVING COUNT(DISTINCT team_position) = 5 ORDER BY champion_name;`

**Resultado (executou, 100 linhas):** [['Aatrox'], ['Akshan'], ['Ambessa']]

**Minha dúvida:** Contou a posição vazia (4 linhas no banco) como se fosse uma sexta posição e devolveu 100 campeões; com as 5 posições válidas são 102. Erro pequeno.

**Sua resposta:** [ ] aceitável  [ ] errada
