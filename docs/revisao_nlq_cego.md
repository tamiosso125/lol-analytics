# Revisão do conjunto cego (perguntas 51–100)

Gerado de `reports/nlq_cego_resultado.json` (2026-11-05T00:23:25). Hashes do sistema: {'src/nlq/route.py': '53d5710f0234240d', 'src/nlq/sql_guard.py': '0e4017057c4baf2d', 'src/nlq/nl_to_sql.py': '1680b174bba225b2', 'src/nlq/schema_context.py': '985fe98508cd925c'}. Commit-base: 66bfe7a.

Como julgar cada pergunta (escreva a letra em **Veredito**):

- **C** = certa (SQL e linhas respondem o que foi perguntado)
- **E** = errada (responde outra coisa, número incoerente, base errada)
- **P** = parcial (certa em parte; ex.: faltou filtro, ordem ou recorte)
- **RC** = recusa certa (o banco não tem o dado e o sistema disse isso)
- **RE** = recusa errada (o banco tinha o dado e o sistema recusou)
- Pergunta ambígua (sem dizer solo ou competitivo): só conta como C se a resposta declarar a base ou mostrar as duas.

Não corrigimos o sistema depois desta folha: o número vai ao TCC como saiu.

## Placar (conferido contra o banco)

- Certas (C): 24; recusas certas (RC): 6; parciais (P): 11; erradas (E): 8; recusas erradas (RE): 1.
- **Acerto estrito (C + RC): 30/50.** Com parciais valendo metade: 35.5/50. Erro ou recusa errada: 9/50.
- Revisão de 5/11: a 89 passou de RC para P (ver o veredito).
- Os vereditos estão em `reports/nlq_cego_vereditos.json`.

---

## 51. Qual foi o campeão com a maior taxa de banimento em 2026?

Roteamento: **solo** (origem: regras), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT c.champion_name
FROM bans b
JOIN matches m ON m.match_id = b.match_id
JOIN (SELECT DISTINCT champion_id, champion_name FROM participants) c
  ON c.champion_id = b.champion_id
WHERE EXTRACT(YEAR FROM m.game_creation) = 2026
GROUP BY c.champion_name
ORDER BY COUNT(DISTINCT b.match_id)::float / (SELECT COUNT(*) FROM matches WHERE EXTRACT(YEAR FROM game_creation) = 2026) DESC
LIMIT 1;
```
Linhas: 1. Colunas: champion_name

- Locke

**Veredito: C** — Locke (id 805) tem taxa de banimento 42,6% em 2026; confere.

---

## 52. Quais foram os 5 campeões menos utilizados na posição JUNGLE?

Roteamento: **solo** (origem: regras), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT champion_name, COUNT(*) AS jogos
FROM participants
WHERE team_position = 'JUNGLE'
GROUP BY champion_name
HAVING COUNT(*) >= 1
ORDER BY jogos ASC
LIMIT 5;
```
Linhas: 5. Colunas: champion_name, jogos

- Cassiopeia | 1
- Aphelios | 1
- Aurora | 1
- Caitlyn | 1
- Illaoi | 1

**Veredito: P** — Há 14 campeões com 1 jogo na JUNGLE (e 47 com 0 jogos, que a consulta ignora); os 5 mostrados são um corte arbitrário do empate, sem avisar.

---

## 53. Qual campeão teve a maior média de mortes por partida?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT champion_name, AVG(deaths) AS media_mortes
FROM participants
GROUP BY champion_name
ORDER BY media_mortes DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: champion_name, media_mortes

- Karthus | 7.7822847682119205

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.champion, AVG(pp.deaths) AS media_mortes
FROM pro_players pp
GROUP BY pp.champion
ORDER BY media_mortes DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: champion, media_mortes

- Briar | 5.7307692307692308

**Veredito: C** — Solo: Karthus 7,78 (2.416 jogos). Competitivo: Briar 5,73 (26 jogos); mesmo topo com filtro de amostra. Declara as duas bases.

---

## 54. Quais foram os 10 campeões com maior média de dano causado?

Roteamento: **solo** (origem: regras), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT champion_name, AVG(dmg_to_champions) AS media_dano
FROM participants
GROUP BY champion_name
HAVING COUNT(*) >= 20
ORDER BY media_dano DESC NULLS LAST
LIMIT 10;
```
Linhas: 10. Colunas: champion_name, media_dano

- Karthus | 34164.921771523179
- KogMaw | 29424.064327485380
- Ezreal | 27301.629157175399
- Ziggs | 27228.965691788526
- Viktor | 26447.690202391904
- Zed | 26348.601220188575

**Veredito: C** — Os 10 campeões e as médias de dano conferem (amostra >= 20).

---

## 55. Qual campeão apresentou a maior média de CS aos 15 minutos?

Roteamento: **solo** (origem: regras), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT 'não é possível responder: o schema não contém estado da partida em um minuto específico (CS aos 15 minutos). A tabela participants só armazena cs_total (CS final da partida), não CS em instantes intermediários.' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: o schema não contém estado da partida em um minuto específico (CS aos 15 minutos). A tabela participants só armazena cs_total (CS final da partida), não CS em instantes intermediários.

**Veredito: RC** — participants só tem cs_total (colunas conferidas); não há CS aos 15 minutos no solo.

---

## 56. Qual foi o campeão mais escolhido pelo lado azul?

Roteamento: **solo** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.champion_name, COUNT(*) AS escolhas
FROM participants p
WHERE p.team_id = 100
GROUP BY p.champion_name
ORDER BY escolhas DESC
LIMIT 1;
```
Linhas: 1. Colunas: champion_name, escolhas

- Jayce | 4125

**Veredito: C** — Jayce, 4.125 escolhas no lado azul (team_id 100); confere.

---

## 57. Qual foi o campeão mais escolhido pelo lado vermelho?

Roteamento: **solo** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.champion_name, COUNT(*) AS escolhas
FROM participants p
WHERE p.team_id = 200
GROUP BY p.champion_name
ORDER BY escolhas DESC
LIMIT 1;
```
Linhas: 1. Colunas: champion_name, escolhas

- Sylas | 3626

**Veredito: C** — Sylas, 3.626 escolhas no lado vermelho (team_id 200); confere.

---

## 58. Quais campeões tiveram mais de 100 partidas disputadas em 2026?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT champion_name, COUNT(*) AS partidas
FROM participants p
JOIN matches m ON m.match_id = p.match_id
WHERE EXTRACT(YEAR FROM m.game_creation) = 2026
GROUP BY champion_name
HAVING COUNT(*) > 100
ORDER BY partidas DESC
LIMIT 100;
```
Linhas: 100. Colunas: champion_name, partidas

- Jayce | 7336
- LeeSin | 7201
- Sylas | 7192
- Ezreal | 6585
- Nautilus | 6572
- Yone | 6011

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.champion, COUNT(*) AS partidas
FROM pro_players pp
JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
WHERE pg.year = 2026
GROUP BY pp.champion
HAVING COUNT(*) > 100
ORDER BY partidas DESC;
```
Linhas: 93. Colunas: champion, partidas

- Xin Zhao | 1730
- Ryze | 1644
- Ezreal | 1628
- Yunara | 1523
- Jarvan IV | 1514
- Rumble | 1400

**Veredito: P** — Solo: 173 campeões passam de 100 partidas, mas o LIMIT 100 corta a lista em 100. Competitivo: 93, completo.

---

## 59. Qual campeão apresentou a maior média de ouro obtido por minuto?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.champion_name, AVG(p.gold_earned / (m.game_duration_s / 60.0)) AS ouro_por_minuto
FROM participants p
JOIN matches m ON m.match_id = p.match_id
GROUP BY p.champion_name
HAVING COUNT(*) >= 20
ORDER BY ouro_por_minuto DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: champion_name, ouro_por_minuto

- Draven | 541.7881523748208189

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 'não é possível responder: pro_players só tem kills, deaths e assists; não há dados de ouro total ou ouro por minuto no schema competitivo' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_players só tem kills, deaths e assists; não há dados de ouro total ou ouro por minuto no schema competitivo

**Veredito: C** — Solo: Draven 541,8 ouro/min (1.955 jogos). Competitivo: recusa correta (pro não tem ouro total).

---

## 60. Qual foi o campeão com a maior taxa de vitória em partidas com duração inferior a 30 minutos?

Roteamento: **solo** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.champion_name, AVG(p.win::int) AS win_rate
FROM participants p
JOIN matches m ON m.match_id = p.match_id
WHERE m.game_duration_s < 1800
GROUP BY p.champion_name
HAVING COUNT(*) >= 20
ORDER BY win_rate DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: champion_name, win_rate

- Ivern | 0.55890410958904109589

**Veredito: C** — Ivern, 55,9% em partidas < 30 min (730 jogos); confere.

---

## 61. Qual jogador apresentou a maior média de eliminações por partida?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, AVG(p.kills) AS media_kills
FROM participants p
GROUP BY p.puuid
HAVING COUNT(*) >= 20
ORDER BY media_kills DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: puuid, media_kills

- vrk5DTvwEVYyv6IC4VYMhLwBgLAlLjyaoclN61dJ0cnvVZoTXZlwakFrpsiX7QV4azEjZMcTBbShPA | 13.4000000000000000

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.player_name, AVG(pp.kills) AS media_eliminacoes
FROM pro_players pp
GROUP BY pp.player_name
HAVING COUNT(*) >= 10
ORDER BY media_eliminacoes DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: player_name, media_eliminacoes

- F8 ice | 9.2142857142857143

**Veredito: C** — Solo: 13,40 de média (40 jogos); competitivo: F8 ice 9,21 (14 jogos). Identifica o jogador por puuid, sem nome.

---

## 62. Quais foram os 5 jogadores com maior quantidade de mortes em 2026?

Roteamento: **solo** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, p.deaths
FROM participants p
JOIN matches m ON m.match_id = p.match_id
WHERE EXTRACT(YEAR FROM m.game_creation) = 2026
ORDER BY p.deaths DESC
LIMIT 5;
```
Linhas: 5. Colunas: puuid, deaths

- UQee_dl6FsRUJXaf71dXMGyN6pODhdv0nSt2U_PY-aQYIA4chWnkPgB0grTTGUyLcqk-q7v2TB08CQ | 25
- Uq_wgWv3bHoH9YQQTsRxMc0QvH63ghLkXCI9GzQtTpQFhlxHF3lxcR0BLF7NurJeRfBjxIkKj4D7TA | 24
- 9BVW5gYI6IAf1DupnUfT5v-0wfhEq-rzA4ZyPVD_BVOuRq7y9bSiixaDUH0Dr45hLB9l8yymJ0LdxA | 24
- dTRej2L3ie28scnMydwB2UsDopMvQj3Bh-W49_aBVMRI12JIVp3zLbnvmrGGV-KMbHWx76-gPqmxhQ | 23
- nr2Zvx-8lmYi-YyiFIvICQqR-P-bQsC0nJSAPicu0qmJozPNMiVGKxeLQeimCR5pwImRdmOAWfJjog | 22

**Veredito: E** — 'Maior quantidade de mortes em 2026' por jogador é a SOMA no ano (1º tem 1.934 mortes em 282 jogos). A consulta ordenou partidas individuais (máximo 25) e pode repetir o mesmo jogador.

---

## 63. Qual jogador conseguiu a maior quantidade de assistências em uma única partida?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, pl.game_name, pl.tag_line, p.assists
FROM participants p
LEFT JOIN players pl ON pl.puuid = p.puuid
ORDER BY p.assists DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: puuid, game_name, tag_line, assists

- nMJi0-sEk4scmXfiIfTm7Pyx6J6dEwjtsjc7w0impkDtcMUaBcc2xLLEc_ywi2bJBrCEiSTBEOcDNQ | None | None | 51

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.player_name, pp.assists
FROM pro_players pp
ORDER BY pp.assists DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: player_name, assists

- Nyph | 45

**Veredito: C** — Solo: 51 assistências; competitivo: Nyph, 45; ambos os máximos conferem.

---

## 64. Qual foi o jogador com maior média de CS por minuto na posição ADC?

Roteamento: **solo** (origem: regras), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, AVG(p.cs_total::float / (m.game_duration_s::float / 60)) AS cs_per_minute
FROM participants p
JOIN matches m ON m.match_id = p.match_id
WHERE p.team_position = 'BOTTOM'
GROUP BY p.puuid
HAVING COUNT(*) >= 20
ORDER BY cs_per_minute DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: puuid, cs_per_minute

- EHg-5BLLSTFAI12jwVZ4u5iK6AWo414QLeKu6BsB_x0vXo5jbxUTqJT4Ws_WtSp9QbTy4zsfRmatBQ | 10.206971558571718

**Veredito: C** — ADC = BOTTOM; 10,207 CS/min com 33 jogos; confere.

---

## 65. Quais jogadores tiveram uma taxa de vitória superior a 70% em 2026, considerando pelo menos 20 partidas?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, p.game_name, AVG(pa.win::int) AS win_rate, COUNT(*) AS partidas
FROM players p
JOIN participants pa ON pa.puuid = p.puuid
JOIN matches m ON m.match_id = pa.match_id
WHERE EXTRACT(YEAR FROM m.game_creation) = 2026
GROUP BY p.puuid, p.game_name
HAVING COUNT(*) >= 20 AND AVG(pa.win::int) > 0.7
ORDER BY win_rate DESC NULLS LAST
LIMIT 100;
```
Linhas: 100. Colunas: puuid, game_name, win_rate, partidas

- hL0diL2TxVOEoSFKnuZ6oI5OJBb7js9b_c0NVhMaVBQKd22NCEVI-ZYxyM_MlqymhaO8A_pp4qBCdQ | None | 0.90909090909090909091 | 22
- vrk5DTvwEVYyv6IC4VYMhLwBgLAlLjyaoclN61dJ0cnvVZoTXZlwakFrpsiX7QV4azEjZMcTBbShPA | CBrayanB | 0.87500000000000000000 | 40
- Ba6rn4f-fJdupD7g6I-AB3ji3kowPpa_HRF38C9oVhiFNmuNVvPlF1jCRevWRnVlDfjwE3qHlwS_Ew | None | 0.85714285714285714286 | 21
- 7YvkNmvHTT-ZCtH3wVwIWPXrdy6R13t8xWTmpyYLHLVIc5X0H8e0Ea-Hio1lIssl_JY0h_zSGLZu0w | Kuroyuuko | 0.82608695652173913043 | 23
- lDklC2YGZxjbqC4GzNkZXt27zqFeUKKuL2a-g4wKfmqR-0AZSBJSW0Je8fY9To9zau6cVETw4k32RQ | sandman | 0.82500000000000000000 | 40
- SGkdUpzf9pUCvXWKEaQvcnDf02nhmcfMrxzPtQhEwws4tCif9yjzveZ6u7JSUhQvKgfZXK-O0dWNvA | None | 0.81818181818181818182 | 22

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.player_name, AVG(pp.win::int) AS win_rate, COUNT(*) AS partidas
FROM pro_players pp
JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
WHERE pg.year = 2026
GROUP BY pp.player_name
HAVING COUNT(*) >= 20 AND AVG(pp.win::int) > 0.7
ORDER BY AVG(pp.win::int) DESC NULLS LAST
LIMIT 100;
```
Linhas: 89. Colunas: player_name, win_rate, partidas

- Gavotto | 0.87500000000000000000 | 24
- Oddie | 0.87500000000000000000 | 24
- Shiku | 0.87500000000000000000 | 24
- Zothve | 0.87500000000000000000 | 24
- Ivory | 0.87500000000000000000 | 24
- Erdote | 0.84313725490196078431 | 51

**Veredito: P** — Solo: 103 jogadores atendem o critério, mas o LIMIT 100 corta 3. Competitivo: 89, completo.

---

## 66. Qual jogador apresentou a maior média de dano causado por minuto?

Roteamento: **solo** (origem: regras), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, pl.game_name, pl.tag_line,
       AVG(p.dmg_to_champions / (m.game_duration_s / 60.0)) AS dmg_per_minute
FROM participants p
JOIN matches m ON m.match_id = p.match_id
JOIN players pl ON pl.puuid = p.puuid
WHERE pl.game_name IS NOT NULL
GROUP BY p.puuid, pl.game_name, pl.tag_line
HAVING COUNT(*) >= 20
ORDER BY dmg_per_minute DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: puuid, game_name, tag_line, dmg_per_minute

- SLrWJww5lbFgrRY7q--53gpF8106YEIm7DuEtGJ3WVPg-nxDRhlqr-g4vI6o_DIPJZbxlBxb6vMEOg | MATHECO | IDGAF | 1324.6583835480904689

**Veredito: C** — 1.324,7 de dano/min (78 jogos); mesmo topo sem exigir nome cadastrado.

---

## 67. Qual foi o jogador com maior quantidade de partidas sem nenhuma morte?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, COUNT(*) AS partidas_sem_morte
FROM participants p
WHERE p.deaths = 0
GROUP BY p.puuid
HAVING COUNT(*) >= 20
ORDER BY partidas_sem_morte DESC
LIMIT 1;
```
Linhas: 1. Colunas: puuid, partidas_sem_morte

- oTG2WJlXq5-uLku7ar1UNkenKsdQ5FNz2V6orFMGoJ84LqkLTloS1cdSpsSwm62RR_5e0pLL0fdung | 47

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.player_name, COUNT(*) AS partidas
FROM pro_players pp
WHERE pp.deaths = 0
GROUP BY pp.player_name
ORDER BY partidas DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: player_name, partidas

- Rekkles | 306

**Veredito: C** — Solo: 47 partidas sem morte; competitivo: Rekkles, 306.

---

## 68. Quais foram os 5 jogadores com maior média de ouro obtido por partida?

Roteamento: **solo** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, AVG(p.gold_earned) AS media_ouro
FROM participants p
GROUP BY p.puuid
HAVING COUNT(*) >= 20
ORDER BY media_ouro DESC NULLS LAST
LIMIT 5;
```
Linhas: 5. Colunas: puuid, media_ouro

- orzvaQTlgCxm9tOpbraJUkgK3p0sU_rqWQ9CKr7W3PZNDA29vlW2_lAeXRT7Qttb_s9BEiGGyFuruA | 17156.880000000000
- R_uv4I_v3HeP93-dKhYeJHUtHlu9MHpjkbTE_aMvM-Vu_MJqQOO6v68fm5s2WTWWFzE5VerwB85JOw | 16367.083333333333
- lDklC2YGZxjbqC4GzNkZXt27zqFeUKKuL2a-g4wKfmqR-0AZSBJSW0Je8fY9To9zau6cVETw4k32RQ | 16124.250000000000
- G1sK1bTbkQEX4ihAmhlf_v_b6I72gFre6tCQXJNtdvspO3h5VtA6D1CRkqudNTU3JVCKwLDxOeh1mQ | 16053.000000000000
- gYIA8UlKlijlRDH4iW3ylb1uaBIaSK_XxR6Zxic5a-4aQBDJRjQ7R_YKCQ42Glz2L85-ERaesCAOwA | 15831.782608695652

**Veredito: C** — Os 5 jogadores e as médias de ouro conferem (>= 20 jogos).

---

## 69. Qual jogador apresentou o maior KDA em uma única partida, considerando apenas partidas com pelo menos uma morte?

Roteamento: **solo** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 2)

```sql
SELECT 
  p.puuid,
  pl.game_name,
  pl.tag_line,
  p.champion_name,
  p.kills,
  p.deaths,
  p.assists,
  ((p.kills + p.assists)::float / p.deaths) AS kda
FROM participants p
LEFT JOIN players pl ON pl.puuid = p.puuid
WHERE p.deaths >= 1
ORDER BY kda DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: puuid, game_name, tag_line, champion_name, kills, deaths, assists, kda

- g6wRXv5vj98pgGOoBTSmzxgaxFF7rhScHZ1V2-Cv4XBAhkhSV8jXJkfA5o-ASkXzNstHbva4aRuxwg | None | None | Zac | 16 | 1 | 26 | 42.0

**Veredito: C** — Zac 16/1/26, KDA 42,0; sem empate no topo.

---

## 70. Qual foi o jogador com maior número de campeões diferentes utilizados em 2026?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT p.puuid, COUNT(DISTINCT p.champion_id) AS campeoes_diferentes
FROM participants p
JOIN matches m ON m.match_id = p.match_id
WHERE EXTRACT(YEAR FROM m.game_creation) = 2026
GROUP BY p.puuid
ORDER BY campeoes_diferentes DESC
LIMIT 1;
```
Linhas: 1. Colunas: puuid, campeoes_diferentes

- CmSvbaGrgTmelntwIPuuP7Q7j8xBUebVhHKLduBA5CH2J9Le2vDvo7dbSBKVlecvlaL7O2hVX0u-rg | 65

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.player_name, COUNT(DISTINCT pp.champion) AS campeoes_diferentes
FROM pro_players pp
JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
WHERE pg.year = 2026
GROUP BY pp.player_name
ORDER BY campeoes_diferentes DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: player_name, campeoes_diferentes

- Envy | 43

**Veredito: C** — Solo: 65 campeões distintos em 2026; competitivo: Envy, 43; conferem.

---

## 71. Qual equipe apresentou a menor taxa de vitória em 2026?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT team_name, AVG(win::int) AS win_rate
FROM pro_games
WHERE year = 2026
GROUP BY team_name
ORDER BY win_rate ASC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: team_name, win_rate

- REDPack Esports | 0E-20

**Veredito: P** — 0% é de fato o mínimo, mas há várias equipes com 0 vitória; a mostrada (REDPack) tem só 4 jogos. Com >= 10 jogos o topo é GLORE (14 jogos, 0%). Escolha arbitrária de empate com amostra minúscula.

---

## 72. Quais foram as 5 equipes com maior média de mortes por partida?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.team_name, AVG(pp.deaths) AS media_mortes
FROM pro_players pp
GROUP BY pp.team_name
ORDER BY media_mortes DESC NULLS LAST
LIMIT 5;
```
Linhas: 5. Colunas: team_name, media_mortes

- Silver Wolves | 7.1333333333333333
- Team Revolta | 7.0000000000000000
- Team Strix | 6.9000000000000000
- ERL Rejects | 6.8000000000000000
- Cute Cats | 6.6000000000000000

**Veredito: E** — Calculou a média por LINHA DE JOGADOR (AVG(pp.deaths)), não por equipe e partida; sem filtro de amostra (Silver Wolves = 15 linhas, 3 jogos) e sem ano.

---

## 73. Qual equipe apresentou a maior média de torres destruídas por partida?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pg.team_name, AVG(pg.towers) AS media_torres
FROM pro_games pg
WHERE pg.year = 2026
GROUP BY pg.team_name
ORDER BY media_torres DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: team_name, media_torres

- Guasones | 9.0000000000000000

**Veredito: P** — Guasones 9,0 vem de 7 jogos; com >= 10 jogos em 2026 o topo é Fuego (8,88). Literalmente é o máximo, mas sem filtro de amostra.

---

## 74. Qual equipe teve a maior sequência de vitórias consecutivas em 2026?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT team_name, COUNT(*) AS vitórias_consecutivas
FROM (
  SELECT team_name, game_id, game_date,
         ROW_NUMBER() OVER (PARTITION BY team_name ORDER BY game_date) -
         ROW_NUMBER() OVER (PARTITION BY team_name, win ORDER BY game_date) AS grp
  FROM pro_games
  WHERE year = 2026 AND win = true
) t
GROUP BY team_name, grp
ORDER BY vitórias_consecutivas DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: team_name, vitórias_consecutivas

- Bilibili Gaming | 82

**Veredito: E** — Filtrou win = true ANTES de agrupar, então as derrotas não quebram a sequência: o 82 do Bilibili é o total de vitórias. A maior sequência real em 2026 é 23 (FENNEL).

---

## 75. Qual equipe apresentou a maior sequência de derrotas consecutivas?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 'não é possível responder: pro_games não registra a ordem cronológica das partidas de uma equipe (não há timestamp ou sequência de jogo). Sem saber qual partida veio antes da outra, não é possível identificar sequências consecutivas de derrotas.' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_games não registra a ordem cronológica das partidas de uma equipe (não há timestamp ou sequência de jogo). Sem saber qual partida veio antes da outra, não é possível identificar sequências consecutivas de derrotas.

**Veredito: RE** — Recusou dizendo que pro_games não tem ordem cronológica, mas tem game_date. Resposta real em 2026: ROSSMANN Centaurs, 23 derrotas seguidas (todos os anos: DRX Academy, 58).

---

## 76. Quais equipes tiveram mais de 50 partidas disputadas durante a temporada?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT team_name, COUNT(DISTINCT game_id) AS partidas
FROM pro_games
GROUP BY team_name
HAVING COUNT(DISTINCT game_id) > 50
ORDER BY partidas DESC;
```
Linhas: 867. Colunas: team_name, partidas

- KT Rolster | 1284
- Dplus Kia | 1127
- Bilibili Gaming | 1115
- JD Gaming | 1106
- EDward Gaming | 1099
- Top Esports | 1092

**Veredito: E** — 'Durante a temporada' pede 2026: 92 equipes têm mais de 50 jogos. A consulta não filtrou o ano e devolveu 867 (todos os anos).

---

## 77. Qual equipe apresentou a maior média de CS total por partida?

Roteamento: **competitivo** (origem: modelo), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 'não é possível responder: pro_games e pro_players não contêm CS total — apenas cs_diff_at15 (diferença de CS aos 15 minutos)' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_games e pro_players não contêm CS total — apenas cs_diff_at15 (diferença de CS aos 15 minutos)

**Veredito: RC** — O competitivo não tem CS total, só cs_diff_at15.

---

## 78. Qual equipe venceu mais partidas jogando pelo lado vermelho?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT team_name, COUNT(*) AS vitórias
FROM pro_games
WHERE side = 'Red' AND win = true
GROUP BY team_name
ORDER BY vitórias DESC
LIMIT 1;
```
Linhas: 1. Colunas: team_name, vitórias

- Gen.G | 352

**Veredito: C** — Gen.G, 352 vitórias do lado vermelho (sem ano na pergunta, todos os anos).

---

## 79. Qual equipe apresentou a maior taxa de vitória jogando pelo lado azul?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pg.team_name, AVG(pg.win::int) AS win_rate
FROM pro_games pg
WHERE pg.side = 'Blue'
GROUP BY pg.team_name
HAVING COUNT(*) >= 10
ORDER BY win_rate DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: team_name, win_rate

- LDM Mexico | 0.92857142857142857143

**Veredito: C** — LDM Mexico, 92,9% (14 jogos no lado azul); confere.

---

## 80. Qual equipe apresentou a maior diferença média de eliminações em relação aos adversários?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.team_name, AVG(pp.kills - pp.deaths) AS diff_media_eliminacoes
FROM pro_players pp
GROUP BY pp.team_name
ORDER BY diff_media_eliminacoes DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: team_name, diff_media_eliminacoes

- 24 7 Tower Dive | 3.0000000000000000

**Veredito: E** — Calculou AVG(kills - deaths) por linha de jogador (escala de 1/5), sem comparar com o adversário e sem amostra (24 7 Tower Dive = 5 linhas, 1 jogo). Diferença real por jogo (>= 50 jogos): Frites Esports Club, +11,45.

---

## 81. Qual foi a média de dragões conquistados por partida em 2026?

Roteamento: **ambos** (origem: modelo), pistas: None

### Base SOLO QUEUE  (tentativas: 1)

```sql
SELECT AVG(t.dragons) AS media_dragoes
FROM matches m
JOIN teams t ON t.match_id = m.match_id
WHERE EXTRACT(YEAR FROM m.game_creation) = 2026;
```
Linhas: 1. Colunas: media_dragoes

- 1.7367946813433018

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT AVG(dragons) AS media_dragoes_por_partida
FROM pro_games
WHERE year = 2026;
```
Linhas: 1. Colunas: media_dragoes_por_partida

- 2.2101530124322601

**Veredito: P** — Responde por EQUIPE (solo 1,74; competitivo 2,21). Por partida, somando as duas equipes, seriam 3,47 e 4,42. A resposta não diz que é por equipe.

---

## 82. Quantas partidas terminaram sem nenhuma equipe conquistar o Barão Nashor?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT COUNT(DISTINCT game_id) AS partidas_sem_barao
FROM pro_games
WHERE barons = 0;
```
Linhas: 1. Colunas: partidas_sem_barao

- 86699

**Veredito: E** — Contou jogos em que ALGUMA das duas equipes tem 0 barões: 86.699. Jogos sem barão de nenhuma equipe: 6.633.

---

## 83. Qual foi a porcentagem de partidas em que a equipe vencedora conquistou o primeiro sangue?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 'não é possível responder: pro_games e pro_players não contêm informação sobre quem conquistou o primeiro sangue (first blood). Apenas kills, deaths e assists totais estão disponíveis.' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_games e pro_players não contêm informação sobre quem conquistou o primeiro sangue (first blood). Apenas kills, deaths e assists totais estão disponíveis.

**Veredito: RC** — O competitivo não registra primeiro sangue.

---

## 84. Qual foi a média de torres destruídas pelas equipes vencedoras?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT AVG(towers) AS media_torres_vencedoras
FROM pro_games
WHERE win = true;
```
Linhas: 1. Colunas: media_torres_vencedoras

- 9.2965923178487558

**Veredito: C** — 9,2966 torres por equipe vencedora (99.217 linhas); confere.

---

## 85. Qual foi a maior quantidade de eliminações registrada por uma equipe em uma única partida?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT MAX(kills) AS maior_quantidade_eliminacoes
FROM pro_games;
```
Linhas: 1. Colunas: maior_quantidade_eliminacoes

- 74

**Veredito: C** — Máximo de 74 eliminações (aNc Outplayed, 2019); confere.

---

## 86. Quantas partidas tiveram mais de 40 eliminações somando as duas equipes?

**Resultado: ERRO TOTAL** (validacao)

Causa: Múltiplos statements não são permitidos.

**Veredito: E** — Erro total: o validador barrou ('Múltiplos statements'). Valor real: 11.547 jogos.

---

## 87. Qual foi a quantidade média de Barões Nashor conquistados pelas equipes vencedoras?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT AVG(pg.barons) AS media_barons_vencedoras
FROM pro_games pg
WHERE pg.win = true;
```
Linhas: 1. Colunas: media_barons_vencedoras

- 1.1269786821900947

**Veredito: C** — 1,1270 barões por equipe vencedora; confere.

---

## 88. Qual foi a porcentagem de vitórias das equipes que conquistaram o primeiro Arauto do Vale?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 'não é possível responder: pro_games não contém informação sobre quem conquistou o primeiro Arauto do Vale, apenas a contagem total de Arautos (heralds) ao final da partida' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_games não contém informação sobre quem conquistou o primeiro Arauto do Vale, apenas a contagem total de Arautos (heralds) ao final da partida

**Veredito: RC** — O competitivo só tem a contagem de arautos, não quem pegou o primeiro.

---

## 89. Qual foi a maior diferença de ouro registrada entre duas equipes ao final de uma partida?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 'não é possível responder: pro_games só tem a DIFERENÇA de ouro aos 15 minutos (gold_diff_at15), não o ouro total das equipes ao final da partida' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_games só tem a DIFERENÇA de ouro aos 15 minutos (gold_diff_at15), não o ouro total das equipes ao final da partida

**Veredito: P** — O roteador mandou a pergunta só ao competitivo, que de fato não tem ouro final, e o sistema recusou. Mas o solo responde: a maior diferença de ouro entre os dois times ao final de uma partida é 21.923 (EUW1_7976698876). Revisado em 5/11 ao comparar com a versão anterior, que respondeu pelo solo.

---

## 90. Quantas partidas terminaram com uma diferença de eliminações inferior a 5 entre as equipes?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT COUNT(DISTINCT pg.game_id) AS partidas
FROM pro_games pg
JOIN pro_players pp ON pp.game_id = pg.game_id AND pp.side = pg.side
GROUP BY pg.game_id
HAVING ABS(SUM(CASE WHEN pg.side = 'Blue' THEN pp.kills ELSE -pp.kills END)) < 5;
```
Linhas: 14946. Colunas: partidas

- 1
- 1
- 1
- 1
- 1
- 1

**Veredito: P** — O número certo (14.946) aparece apenas como QUANTIDADE DE LINHAS: a consulta agrupou por jogo e devolveu 14.946 linhas com o valor 1, em vez de uma contagem.

---

## 91. Qual liga apresentou a maior taxa média de banimento de campeões em 2026?

Roteamento: **competitivo** (origem: modelo), pistas: None

### Base COMPETITIVO  (tentativas: 2)

```sql
SELECT 'não é possível responder: pro_games e pro_players não contêm dados de banimentos; bans existe apenas em solo queue (matches/teams/participants)' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_games e pro_players não contêm dados de banimentos; bans existe apenas em solo queue (matches/teams/participants)

**Veredito: RC** — O competitivo não tem banimentos (colunas conferidas); o solo tem bans mas não tem liga.

---

## 92. Quais foram as 5 ligas com maior número de equipes participantes?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT league, COUNT(DISTINCT team_name) AS num_equipes
FROM pro_games
GROUP BY league
ORDER BY num_equipes DESC
LIMIT 5;
```
Linhas: 5. Colunas: league, num_equipes

- EM | 135
- EUM | 113
- WLDs | 113
- UPL | 110
- NACL | 92

**Veredito: C** — EM 135, EUM 113, WLDs 113, UPL 110, NACL 92 (todos os anos); confere.

---

## 93. Qual liga apresentou a menor duração média das partidas?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pg.league, AVG(pg.game_length_s) AS duracao_media
FROM pro_games pg
GROUP BY pg.league
ORDER BY duracao_media ASC
LIMIT 1;
```
Linhas: 1. Colunas: league, duracao_media

- LGL | 1577.6250000000000000

**Veredito: P** — LGL (1.577 s) vem de apenas 8 jogos; com >= 100 jogos a menor duração é PCL (1.667 s). Sem filtro de amostra.

---

## 94. Qual foi o campeão mais banido em cada uma das principais ligas profissionais?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT league, champion, bans
FROM (
  SELECT pg.league, pp.champion, COUNT(*) AS bans,
         ROW_NUMBER() OVER (PARTITION BY pg.league ORDER BY COUNT(*) DESC) AS rn
  FROM pro_players pp
  JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
  WHERE pp.champion IS NOT NULL
  GROUP BY pg.league, pp.champion
) ranked
WHERE rn = 1
ORDER BY league;
```
Linhas: 122. Colunas: league, champion, bans

- AC | Rell | 17
- AL | Nautilus | 275
- AOL | Kai'Sa | 25
- ASCI | Renekton | 77
- ASI | Jarvan IV | 17
- Asia Master | Xin Zhao | 84

**Veredito: E** — Violação de honestidade: o competitivo não tem banimentos; a consulta contou ESCOLHAS (pro_players.champion) e as rotulou como 'bans'. Devia recusar. Também listou 122 ligas em vez das principais.

---

## 95. Qual liga apresentou a maior média de ouro obtido por equipe?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 'não é possível responder: pro_games só tem a DIFERENÇA de ouro aos 15 minutos (gold_diff_at15), não o ouro total obtido por equipe' AS aviso;
```
Linhas: 1. Colunas: aviso

- não é possível responder: pro_games só tem a DIFERENÇA de ouro aos 15 minutos (gold_diff_at15), não o ouro total obtido por equipe

**Veredito: RC** — pro_games só tem gold_diff_at15, não o ouro total.

---

## 96. Quais foram os 5 jogadores com mais eliminações na LCK em 2026?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pp.player_name, SUM(pp.kills) AS total_kills
FROM pro_players pp
JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
WHERE pg.league = 'LCK' AND pg.year = 2026
GROUP BY pp.player_name
ORDER BY total_kills DESC NULLS LAST
LIMIT 5;
```
Linhas: 5. Colunas: player_name, total_kills

- Ruler | 404
- Peyz | 387
- Smash | 378
- Diable | 326
- Chovy | 321

**Veredito: C** — Ruler 404, Peyz 387, Smash 378, Diable 326, Chovy 321; conferem.

---

## 97. Qual equipe apresentou a maior taxa de vitória na LPL em 2026?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT team_name, AVG(win::int) AS win_rate
FROM pro_games
WHERE league = 'LPL' AND year = 2026
GROUP BY team_name
HAVING COUNT(*) >= 10
ORDER BY win_rate DESC NULLS LAST
LIMIT 1;
```
Linhas: 1. Colunas: team_name, win_rate

- Bilibili Gaming | 0.71276595744680851064

**Veredito: C** — Bilibili Gaming, 71,3% (94 jogos); confere.

---

## 98. Qual foi a diferença na duração média das partidas entre a LCK e a LEC?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT 
  pg.league,
  AVG(pg.game_length_s) AS duracao_media_s
FROM pro_games pg
WHERE pg.league IN ('LCK', 'LEC')
GROUP BY pg.league;
```
Linhas: 2. Colunas: league, duracao_media_s

- LCK | 2042.5666791885800150
- LEC | 1974.7860465116279070

**Veredito: P** — Devolveu as duas médias (LCK 2.042,6 s; LEC 1.974,8 s, todos os anos) mas não calculou a diferença (67,8 s).

---

## 99. Qual liga apresentou a maior diversidade de campeões escolhidos durante a temporada?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT pg.league, COUNT(DISTINCT pp.champion) AS campeoes_unicos
FROM pro_games pg
JOIN pro_players pp ON pp.game_id = pg.game_id AND pp.side = pg.side
WHERE pg.year = 2026
GROUP BY pg.league
ORDER BY campeoes_unicos DESC
LIMIT 1;
```
Linhas: 1. Colunas: league, campeoes_unicos

- LJL | 138

**Veredito: C** — LJL, 138 campeões distintos em 2026; confere.

---

## 100. Qual foi a equipe com mais vitórias em cada uma das principais ligas profissionais de 2026?

Roteamento: **competitivo** (origem: regras), pistas: None

### Base COMPETITIVO  (tentativas: 1)

```sql
SELECT league, team_name, wins
FROM (
  SELECT pg.league, pg.team_name, COUNT(*) AS wins,
         ROW_NUMBER() OVER (PARTITION BY pg.league ORDER BY COUNT(*) DESC) AS rn
  FROM pro_games pg
  WHERE pg.year = 2026 AND pg.win = true
  GROUP BY pg.league, pg.team_name
) ranked
WHERE rn = 1;
```
Linhas: 43. Colunas: league, team_name, wins

- AC | FURIA | 8
- AL | FN Esports | 43
- Asia Master | KT Rolster Challengers | 14
- CBLOL | FURIA | 34
- CCWS | G2 NORD | 11
- CD | KaBuM! Ilha das Lendas | 18

**Veredito: P** — Lista as 43 ligas de 2026 em vez das principais, e os empates no 1º lugar saem arbitrários; os campeões por liga estão corretos.

---
