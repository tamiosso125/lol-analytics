"""Gera um conjunto grande de perguntas COM GABARITO (SQL de referência) para a consulta
em linguagem natural.

Por que existe (2026-11-05): os conjuntos anteriores eram julgados por uma pessoa (eu) depois
de ver a saída do sistema, e cada julgamento era único. Aqui a resposta certa nasce junto
da pergunta, antes de qualquer execução do sistema, e quem compara é código
(`src/nlq/avaliar_gabarito.py`). Todas as perguntas são escritas a partir de TEMPLATES sobre
o próprio banco (campeões, equipes, ligas, patches, jogadores reais), então:
  * a SQL de referência é correta por construção e é executada aqui; pergunta cujo gabarito
    falha, vem vazio, estoura o tempo ou tem empate no limite do ranking é DESCARTADA;
  * perguntas que o banco não responde (primeiro sangue, série, ouro aos 10 minutos, dano a
    estruturas, banimento no competitivo...) saem com `recusa_esperada = true` e sem SQL;
  * nenhuma pergunta repete as dos conjuntos anteriores (conferido por texto normalizado).

Limite declarado: perguntas de template são menos variadas que perguntas escritas por uma
pessoa. Este conjunto mede cobertura e regressão em escala; a medida de generalização
continua pedindo perguntas escritas à mão.

Uso:  python -m src.nlq.gerar_gabarito           (grava docs/nlq_gabarito_900.json e
                                                  docs/nlq_perguntas_900.txt)
"""
import json
import os
import random
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import psycopg2

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))
from src import config  # noqa: E402,F401  (carrega o .env)

SEMENTE = 20261105
ALVO = 900
PRIMEIRO_NUMERO = 201
SAIDA_JSON = RAIZ / "docs" / "nlq_gabarito_900.json"
SAIDA_TXT = RAIZ / "docs" / "nlq_perguntas_900.txt"

METRICAS_SOLO = {  # coluna: (rótulo médio, rótulo "quantidade")
    "kills": "eliminações", "deaths": "mortes", "assists": "assistências",
    "dmg_to_champions": "dano causado a campeões", "gold_earned": "ouro obtido",
    "cs_total": "CS total", "vision_score": "pontuação de visão",
}
POSICOES = {"TOP": "TOP", "JUNGLE": "JUNGLE", "MIDDLE": "MIDDLE", "BOTTOM": "BOTTOM", "UTILITY": "UTILITY"}
METRICAS_EQUIPE_PRO = {"kills": "eliminações", "deaths": "mortes", "dragons": "dragões",
                       "barons": "Barões Nashor", "towers": "torres destruídas"}
METRICAS_TEAM_SOLO = {"dragons": "dragões", "barons": "Barões Nashor", "towers": "torres destruídas",
                      "heralds": "Arautos do Vale", "inhibitors": "inibidores destruídos"}


def _q(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def _norm(t: str) -> str:
    sem = unicodedata.normalize("NFKD", t)
    return re.sub(r"\s+", " ", "".join(c for c in sem if not unicodedata.combining(c)).lower()).strip()


def _conn():
    c = psycopg2.connect(os.environ["DATABASE_URL"])
    c.set_session(readonly=True)
    cur = c.cursor()
    cur.execute("SET statement_timeout = 20000")
    return c, cur


def _perguntas_existentes() -> set[str]:
    L = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
    textos = []
    for arq in ("nlq_perguntas_cegas.txt", "nlq_perguntas_v2_novas.txt", "nlq_perguntas_livres_dev.txt"):
        p = RAIZ / "docs" / arq
        if p.exists():
            textos.append(p.read_text(encoding="utf-8"))
    try:
        textos.append(subprocess.run(["git", "show", "HEAD:docs/nlq_perguntas_cegas.txt"], cwd=RAIZ,
                                     capture_output=True).stdout.decode("utf-8"))
    except Exception:
        pass
    out = set()
    for t in textos:
        for linha in t.splitlines():
            m = L.match(linha)
            if m:
                out.add(_norm(m[2]))
    return out


class Gerador:
    def __init__(self):
        self.rng = random.Random(SEMENTE)
        self.conn, self.cur = _conn()
        self.itens: list[dict] = []
        self.descartes: dict[str, int] = {}

    # ---------- infraestrutura ----------
    def consulta(self, sql: str):
        try:
            self.cur.execute(sql)
            return self.cur.fetchall()
        except psycopg2.Error:
            self.conn.rollback()
            self.conn.set_session(readonly=True)
            self.cur.execute("SET statement_timeout = 20000")
            return None

    def add(self, base, familia, pergunta, sql, tipo="escalar", n=None, desempate=None):
        """Registra a pergunta se o gabarito roda, tem linhas e (ranking) não empata no corte."""
        rows = self.consulta(sql)
        if not rows or all(v is None for r in rows for v in r):
            self.descartes[familia] = self.descartes.get(familia, 0) + 1
            return
        if tipo == "ranking" and n:
            # empate no limite deixaria o gabarito ambíguo: confere N+1
            extra = self.consulta(re.sub(r"LIMIT \d+\s*;?\s*$", f"LIMIT {n + 1}", sql.strip()))
            if extra and len(extra) > n and extra[n - 1][-1] == extra[n][-1]:
                self.descartes[familia] = self.descartes.get(familia, 0) + 1
                return
        self.itens.append({"base": base, "familia": familia, "pergunta": pergunta, "sql_ref": sql,
                           "tipo": tipo, "recusa_esperada": False, "n_ref": len(rows)})

    def recusa(self, base, familia, pergunta, motivo):
        self.itens.append({"base": base, "familia": familia, "pergunta": pergunta, "sql_ref": None,
                           "tipo": "recusa", "recusa_esperada": True, "motivo_ref": motivo})

    def pick(self, lst, k):
        lst = list(lst)
        self.rng.shuffle(lst)
        return lst[:k]

    def v(self, *opcoes):
        return self.rng.choice(opcoes)

    # ---------- entidades reais do banco ----------
    def carregar(self):
        s = self.consulta
        self.campeoes_solo = [r[0] for r in s("SELECT champion_name FROM participants GROUP BY 1 HAVING COUNT(*) >= 300 ORDER BY COUNT(*) DESC")]
        self.plataformas = [r[0] for r in s("SELECT platform_id FROM matches GROUP BY 1 HAVING COUNT(*) >= 500")]
        self.tiers = [r[0] for r in s("SELECT tier FROM players WHERE tier IS NOT NULL GROUP BY 1 HAVING COUNT(*) >= 50")]
        self.itens_nome = [r[0] for r in s("""SELECT i.name FROM item_events e JOIN items i ON i.item_id = e.item_id
                                             WHERE e.action = 'BUY' AND i.purchasable AND i.total_gold >= 2000
                                             GROUP BY i.name HAVING COUNT(*) >= 500 ORDER BY COUNT(*) DESC LIMIT 40""")]
        self.equipes = [r[0] for r in s("SELECT team_name FROM pro_games GROUP BY 1 HAVING COUNT(*) >= 60 ORDER BY COUNT(*) DESC LIMIT 120")]
        self.equipes26 = [r[0] for r in s("SELECT team_name FROM pro_games WHERE year = 2026 GROUP BY 1 HAVING COUNT(*) >= 25 ORDER BY COUNT(*) DESC LIMIT 100")]
        self.ligas = [r[0] for r in s("SELECT league FROM pro_games WHERE year = 2026 GROUP BY 1 HAVING COUNT(DISTINCT game_id) >= 60 ORDER BY COUNT(*) DESC")]
        self.patches = [r[0] for r in s("SELECT patch FROM pro_games WHERE year = 2026 GROUP BY 1 HAVING COUNT(DISTINCT game_id) >= 60 ORDER BY patch")]
        self.jogadores = [r[0] for r in s("SELECT player_name FROM pro_players WHERE player_name IS NOT NULL GROUP BY 1 HAVING COUNT(*) >= 60 ORDER BY COUNT(*) DESC LIMIT 200")]
        self.campeoes_pro = [r[0] for r in s("SELECT champion FROM pro_players GROUP BY 1 HAVING COUNT(*) >= 300 ORDER BY COUNT(*) DESC")]
        self.anos = [r[0] for r in s("SELECT year FROM pro_games GROUP BY 1 HAVING COUNT(DISTINCT game_id) >= 300 ORDER BY 1")]

    # ---------- SOLO ----------
    def solo(self):
        champs = self.campeoes_solo
        for c in self.pick(champs, 70):
            self.add("solo", "S1-winrate-campeao", self.v(f"Qual é a taxa de vitória do campeão {c}?",
                     f"Qual a taxa de vitória de {c} no solo queue?", f"Quanto é o win rate de {c}?"),
                     f"SELECT AVG(win::int) AS taxa FROM participants WHERE champion_name = {_q(c)}")
        for c in self.pick(champs, 40):
            self.add("solo", "S2-partidas-campeao", self.v(f"Quantas partidas o campeão {c} disputou?",
                     f"Quantas vezes {c} foi jogado?"),
                     f"SELECT COUNT(*) AS partidas FROM participants WHERE champion_name = {_q(c)}")
        for col, nome in METRICAS_SOLO.items():
            for c in self.pick(champs, 11):
                self.add("solo", "S3-media-campeao", self.v(f"Qual é a média de {nome} do campeão {c}?",
                         f"Qual a média de {nome} por partida de {c}?"),
                         f"SELECT AVG({col}) AS media FROM participants WHERE champion_name = {_q(c)}")
        for col, nome in list(METRICAS_SOLO.items())[:6]:
            for pos in POSICOES:
                for n in (3, 5):
                    self.add("solo", "S4-top-campeoes-posicao",
                             self.v(f"Quais são os {n} campeões com maior média de {nome} na posição {pos}?",
                                    f"Quais os {n} campeões com a maior média de {nome} jogando de {pos}?"),
                             f"SELECT champion_name, AVG({col}) AS media FROM participants WHERE team_position = {_q(pos)} "
                             f"GROUP BY champion_name HAVING COUNT(*) >= 20 ORDER BY media DESC NULLS LAST LIMIT {n}",
                             tipo="ranking", n=n)
        for pos in POSICOES:
            for variante in range(2):
                self.add("solo", "S5-mais-jogado-posicao",
                         [f"Qual é o campeão mais jogado na posição {pos}?",
                          f"Qual campeão aparece mais vezes de {pos}?"][variante],
                         f"SELECT champion_name, COUNT(*) AS jogos FROM participants WHERE team_position = {_q(pos)} "
                         f"GROUP BY champion_name ORDER BY jogos DESC LIMIT 1", tipo="ranking", n=1)
        for lado, tid in (("azul", 100), ("vermelho", 200)):
            self.add("solo", "S6-lado", f"Qual é a taxa de vitória do time {lado}?",
                     f"SELECT AVG(win::int) AS taxa FROM teams WHERE team_id = {tid}")
            for col, nome in METRICAS_TEAM_SOLO.items():
                self.add("solo", "S6-lado", self.v(f"Qual é a média de {nome} do time {lado} por partida?",
                         f"Quantos {nome} o time {lado} faz em média por partida?"),
                         f"SELECT AVG({col}) AS media FROM teams WHERE team_id = {tid}")
        for m in (20, 25, 30, 35, 40):
            self.add("solo", "S7-duracao", f"Quantas partidas duraram mais de {m} minutos?",
                     f"SELECT COUNT(*) AS partidas FROM matches WHERE game_duration_s > {m * 60}")
            self.add("solo", "S7-duracao", f"Qual é a taxa de vitória do time vermelho em partidas com mais de {m} minutos?",
                     f"SELECT AVG(t.win::int) AS taxa FROM teams t JOIN matches m ON m.match_id = t.match_id "
                     f"WHERE t.team_id = 200 AND m.game_duration_s > {m * 60}")
        self.add("solo", "S7-duracao", "Qual é a duração média das partidas do solo queue, em segundos?",
                 "SELECT AVG(game_duration_s) AS media FROM matches")
        self.add("solo", "S7-duracao", "Qual foi a duração da partida mais longa do solo queue?",
                 "SELECT MAX(game_duration_s) AS maior FROM matches")
        for n in (3, 5, 10):
            self.add("solo", "S8-bans", f"Quais são os {n} campeões mais banidos?",
                     f"SELECT c.champion_name, COUNT(*) AS bans FROM bans b JOIN (SELECT DISTINCT champion_id, champion_name FROM participants) c "
                     f"ON c.champion_id = b.champion_id GROUP BY c.champion_name ORDER BY bans DESC LIMIT {n}", tipo="ranking", n=n)
        for c in self.pick(champs, 30):
            self.add("solo", "S8-bans", self.v(f"Quantas vezes o campeão {c} foi banido?", f"Quantos banimentos {c} recebeu?"),
                     f"SELECT COUNT(*) AS bans FROM bans b JOIN (SELECT DISTINCT champion_id, champion_name FROM participants) c "
                     f"ON c.champion_id = b.champion_id WHERE c.champion_name = {_q(c)}")
        for p in (52, 53, 54, 55, 56):
            self.add("solo", "S9-campeoes-wr", f"Quantos campeões têm taxa de vitória acima de {p}% com pelo menos 100 partidas?",
                     f"SELECT COUNT(*) AS campeoes FROM (SELECT champion_name FROM participants GROUP BY champion_name "
                     f"HAVING COUNT(*) >= 100 AND AVG(win::int) > {p / 100}) s")
        for pl in self.plataformas:
            self.add("solo", "S10-plataforma", f"Quantas partidas foram coletadas na plataforma {pl}?",
                     f"SELECT COUNT(*) AS partidas FROM matches WHERE platform_id = {_q(pl)}")
            self.add("solo", "S10-plataforma", f"Qual é a duração média das partidas na plataforma {pl}?",
                     f"SELECT AVG(game_duration_s) AS media FROM matches WHERE platform_id = {_q(pl)}")
        for t in self.tiers:
            self.add("solo", "S11-jogadores", f"Quantos jogadores do tier {t} estão cadastrados?",
                     f"SELECT COUNT(*) AS jogadores FROM players WHERE tier = {_q(t)}")
        for it in self.pick(self.itens_nome, 25):
            self.add("solo", "S12-itens", self.v(f"Quantas vezes o item {it} foi comprado?", f"Quantas compras do item {it} existem?"),
                     f"SELECT COUNT(*) AS compras FROM item_events e JOIN items i ON i.item_id = e.item_id "
                     f"WHERE i.name = {_q(it)} AND e.action = 'BUY'")
        self.add("solo", "S12-itens", "Qual é o item mais comprado?",
                 "SELECT i.name, COUNT(*) AS compras FROM item_events e JOIN items i ON i.item_id = e.item_id "
                 "WHERE e.action = 'BUY' GROUP BY i.name ORDER BY compras DESC LIMIT 1", tipo="ranking", n=1)
        for c in self.pick(champs, 20):
            self.add("solo", "S14-kda", f"Qual é o KDA médio do campeão {c}?",
                     f"SELECT AVG((kills + assists)::float / NULLIF(deaths, 0)) AS kda FROM participants WHERE champion_name = {_q(c)}")
        for c in self.pick(champs, 35):
            self.add("solo", "S15-posicao-campeao", self.v(f"Em qual posição o campeão {c} mais joga?",
                     f"Qual a posição mais comum de {c}?"),
                     f"SELECT team_position, COUNT(*) AS jogos FROM participants WHERE champion_name = {_q(c)} "
                     f"GROUP BY team_position ORDER BY jogos DESC LIMIT 1", tipo="ranking", n=1)
        for pos in POSICOES:
            self.add("solo", "S16-visao", f"Qual é a pontuação de visão média na posição {pos}?",
                     f"SELECT AVG(vision_score) AS media FROM participants WHERE team_position = {_q(pos)}")

    # ---------- COMPETITIVO ----------
    def competitivo(self):
        for t in self.pick(self.equipes26, 40):
            self.add("competitivo", "C1-winrate-equipe", self.v(f"Qual é a taxa de vitória da equipe {t} em 2026?",
                     f"Qual o aproveitamento de {t} em 2026?"),
                     f"SELECT AVG(win::int) AS taxa FROM pro_games WHERE team_name = {_q(t)} AND year = 2026")
        for t in self.pick(self.equipes, 40):
            self.add("competitivo", "C1-winrate-equipe", self.v(f"Qual é a taxa de vitória da equipe {t}?",
                     f"Qual o win rate de {t} no profissional?"),
                     f"SELECT AVG(win::int) AS taxa FROM pro_games WHERE team_name = {_q(t)}")
        for t in self.pick(self.equipes, 40):
            self.add("competitivo", "C2-jogos-equipe", self.v(f"Quantos jogos a equipe {t} disputou?",
                     f"Quantas partidas {t} jogou?"),
                     f"SELECT COUNT(DISTINCT game_id) AS jogos FROM pro_games WHERE team_name = {_q(t)}")
        for col, nome in METRICAS_EQUIPE_PRO.items():
            for t in self.pick(self.equipes, 14):
                self.add("competitivo", "C3-media-equipe", self.v(f"Qual é a média de {nome} da equipe {t} por jogo?",
                         f"Quantos {nome} {t} faz em média por jogo?"),
                         f"SELECT AVG({col}) AS media FROM pro_games WHERE team_name = {_q(t)}")
        for lg in self.pick(self.ligas, 14):
            self.add("competitivo", "C4-liga", self.v(f"Quantos jogos a {lg} teve em 2026?", f"Quantas partidas foram disputadas na {lg} em 2026?"),
                     f"SELECT COUNT(DISTINCT game_id) AS jogos FROM pro_games WHERE league = {_q(lg)} AND year = 2026")
            self.add("competitivo", "C4-liga", f"Qual é a duração média das partidas da {lg} em 2026, em segundos?",
                     f"SELECT AVG(game_length_s) AS media FROM pro_games WHERE league = {_q(lg)} AND year = 2026")
            self.add("competitivo", "C4-liga", f"Qual é a taxa de vitória do lado azul na {lg} em 2026?",
                     f"SELECT AVG(win::int) AS taxa FROM pro_games WHERE league = {_q(lg)} AND year = 2026 AND side = 'Blue'")
        for j in self.pick(self.jogadores, 30):
            self.add("competitivo", "C5-jogador", self.v(f"Qual é a média de eliminações do jogador {j}?", f"Quantas eliminações {j} faz em média por jogo?"),
                     f"SELECT AVG(kills) AS media FROM pro_players WHERE player_name = {_q(j)}")
            self.add("competitivo", "C5-jogador", f"Quantos jogos o jogador {j} disputou?",
                     f"SELECT COUNT(*) AS jogos FROM pro_players WHERE player_name = {_q(j)}")
        for j in self.pick(self.jogadores, 20):
            self.add("competitivo", "C5-jogador", f"Qual é o KDA médio do jogador {j}?",
                     f"SELECT AVG((kills + assists)::float / NULLIF(deaths, 0)) AS kda FROM pro_players WHERE player_name = {_q(j)}")
        for c in self.pick(self.campeoes_pro, 35):
            self.add("competitivo", "C6-campeao-pro", self.v(f"Quantas vezes o campeão {c} foi escolhido no competitivo?",
                     f"Quantos picks {c} teve no competitivo?"),
                     f"SELECT COUNT(*) AS picks FROM pro_players WHERE champion = {_q(c)}")
            self.add("competitivo", "C6-campeao-pro", f"Qual é a taxa de vitória do campeão {c} no competitivo em 2026?",
                     f"SELECT AVG(pp.win::int) AS taxa FROM pro_players pp JOIN pro_games pg ON pg.game_id = pp.game_id "
                     f"AND pg.side = pp.side WHERE pp.champion = {_q(c)} AND pg.year = 2026")
        for p in self.pick(self.patches, 14):
            self.add("competitivo", "C7-patch", f"Quantos jogos profissionais foram disputados no patch {p}?",
                     f"SELECT COUNT(DISTINCT game_id) AS jogos FROM pro_games WHERE patch = {_q(p)}")
            self.add("competitivo", "C7-patch", f"Qual é a duração média das partidas no patch {p}?",
                     f"SELECT AVG(game_length_s) AS media FROM pro_games WHERE patch = {_q(p)}")
        for n in (3, 5, 10):
            self.add("competitivo", "C8-ranking", f"Quais foram as {n} equipes com mais vitórias em 2026?",
                     f"SELECT team_name, SUM(win::int) AS vitorias FROM pro_games WHERE year = 2026 GROUP BY team_name "
                     f"ORDER BY vitorias DESC LIMIT {n}", tipo="ranking", n=n)
            self.add("competitivo", "C8-ranking", f"Quais foram as {n} ligas com mais jogos em 2026?",
                     f"SELECT league, COUNT(DISTINCT game_id) AS jogos FROM pro_games WHERE year = 2026 GROUP BY league "
                     f"ORDER BY jogos DESC LIMIT {n}", tipo="ranking", n=n)
            self.add("competitivo", "C8-ranking", f"Quais foram os {n} campeões mais escolhidos no competitivo em 2026?",
                     f"SELECT pp.champion, COUNT(*) AS jogos FROM pro_players pp JOIN pro_games pg ON pg.game_id = pp.game_id "
                     f"AND pg.side = pp.side WHERE pg.year = 2026 GROUP BY pp.champion ORDER BY jogos DESC LIMIT {n}", tipo="ranking", n=n)
            self.add("competitivo", "C8-ranking", f"Quais são os {n} jogadores com mais eliminações no total em 2026?",
                     f"SELECT pp.player_name, SUM(pp.kills) AS total FROM pro_players pp JOIN pro_games pg ON pg.game_id = pp.game_id "
                     f"AND pg.side = pp.side WHERE pg.year = 2026 GROUP BY pp.player_name ORDER BY total DESC LIMIT {n}", tipo="ranking", n=n)
        for ano in self.anos:
            self.add("competitivo", "C9-ano", self.v(f"Quantos jogos profissionais foram registrados em {ano}?", f"Quantas partidas profissionais existem em {ano}?"),
                     f"SELECT COUNT(DISTINCT game_id) AS jogos FROM pro_games WHERE year = {ano}")
            self.add("competitivo", "C9-ano", f"Qual foi a duração média das partidas profissionais em {ano}, em segundos?",
                     f"SELECT AVG(game_length_s) AS media FROM pro_games WHERE year = {ano}")
        for mes in range(1, 13):
            self.add("competitivo", "C9-ano", f"Quantos jogos profissionais foram disputados no mês {mes} de 2026?",
                     f"SELECT COUNT(DISTINCT game_id) AS jogos FROM pro_games WHERE year = 2026 AND EXTRACT(MONTH FROM game_date) = {mes}")
        for k in (30, 35, 40, 45, 50):
            self.add("competitivo", "C10-contagem", f"Quantos jogos tiveram mais de {k} eliminações somando as duas equipes?",
                     f"SELECT COUNT(*) AS jogos FROM (SELECT game_id FROM pro_games GROUP BY game_id HAVING SUM(kills) > {k}) s")
        for col, nome in (("dragons", "dragões"), ("towers", "torres"), ("heralds", "Arautos do Vale")):
            for k in (4, 6, 8):
                self.add("competitivo", "C10-contagem", f"Quantos jogos tiveram mais de {k} {nome} somando as duas equipes?",
                         f"SELECT COUNT(*) AS jogos FROM (SELECT game_id FROM pro_games GROUP BY game_id HAVING SUM({col}) > {k}) s")
        for pos in ("top", "jng", "mid", "bot", "sup"):
            self.add("competitivo", "C12-posicao", f"Qual é a média de eliminações da posição {pos} no competitivo?",
                     f"SELECT AVG(kills) AS media FROM pro_players WHERE position = {_q(pos)}")
        for ano in (2023, 2024, 2025, 2026):
            self.add("competitivo", "C11-lado", f"Qual foi a taxa de vitória do lado azul em {ano}?",
                     f"SELECT AVG(win::int) AS taxa FROM pro_games WHERE year = {ano} AND side = 'Blue'")

    # ---------- perguntas SEM resposta no banco ----------
    def sem_resposta(self):
        objs = [("sangue", "o primeiro sangue"), ("torre", "a primeira torre"), ("dragao", "o primeiro dragão"),
                ("barao", "o primeiro Barão Nashor"), ("arauto", "o primeiro Arauto do Vale")]
        for _, o in objs:
            self.recusa("competitivo", "U1-primeiro", f"Qual equipe conquistou {o} mais vezes em 2026?", "primeiro evento ausente")
            self.recusa("competitivo", "U1-primeiro", f"Qual é a taxa de vitória das equipes que conquistaram {o}?", "primeiro evento ausente")
            self.recusa("solo", "U1-primeiro", f"Em quantas partidas o time azul conquistou {o}?", "primeiro evento ausente")
            self.recusa("competitivo", "U1-primeiro", f"Qual liga tem a maior taxa de partidas em que quem fez {o} venceu?", "primeiro evento ausente")
        for f in ("Qual equipe disputou mais séries melhor de cinco em 2026?", "Quantas séries melhor de três terminaram em 2 a 0?",
                  "Qual a taxa de vitória de quem venceu o jogo 1 de uma série?", "Qual equipe virou mais séries depois de perder o primeiro jogo?",
                  "Quantas séries foram decididas no jogo 5?", "Qual equipe tem mais séries vencidas por 3 a 0?",
                  "Qual o aproveitamento de uma equipe em séries melhor de cinco?", "Quantas séries a T1 disputou?"):
            self.recusa("competitivo", "U2-serie", f, "série ausente")
        for minuto in (5, 10, 20, 25):
            for tema in ("a diferença de ouro", "a média de CS", "o número de eliminações", "a vantagem de experiência"):
                self.recusa("competitivo", "U3-minuto", f"Qual era {tema} aos {minuto} minutos, em média?", "estado em minuto ausente")
        for f in ("Qual jogador profissional causou mais dano a campeões?", "Qual equipe tem a maior média de dano por minuto no competitivo?",
                  "Qual jogador profissional tem a maior pontuação de visão?", "Qual a média de wards colocadas por jogo na LCK?",
                  "Qual jogador causou mais dano a torres?", "Qual campeão causa mais dano a estruturas?",
                  "Qual equipe do competitivo tem mais ouro total por partida?", "Qual jogador profissional tem mais CS por minuto?",
                  "Qual a média de CS total das equipes da LPL?", "Qual jogador profissional tem a maior participação no dano da equipe?"):
            self.recusa("competitivo", "U4-dano-visao", f, "dano, visão, ouro total ou CS total ausentes no competitivo")
        for lg in self.pick(self.ligas, 8):
            self.recusa("competitivo", "U5-ban-pro", f"Qual campeão foi mais banido na {lg} em 2026?", "banimentos ausentes no competitivo")
        for f in ("Qual campeão foi escolhido mais vezes como primeira escolha do draft?", "Qual a primeira escolha mais comum da T1?",
                  "Em que ordem os campeões são escolhidos no draft?", "Qual campeão é mais banido na primeira fase de bans do competitivo?",
                  "Qual a taxa de vitória de quem tem a primeira escolha?", "Qual posição costuma ser escolhida primeiro no draft?"):
            self.recusa("competitivo", "U6-draft", f, "ordem do draft ausente")
        for f in ("Qual item o jogador Faker mais compra no competitivo?", "Qual a build mais comum do campeão Ahri no competitivo?",
                  "Qual item mais comprado por equipes vencedoras da LCK?", "Qual o item mais caro comprado no competitivo?",
                  "Quanto ouro a T1 gasta em itens por jogo?", "Qual item mais comprado no competitivo em 2026?"):
            self.recusa("competitivo", "U7-itens-pro", f, "itens ausentes no competitivo")
        for f in ("Quantos pentakills aconteceram no solo queue?", "Quem fez mais pentakills em 2026?", "Qual campeão tem mais pentakills?",
                  "Quantos quadrakills aconteceram no solo queue?", "Qual jogador fez o primeiro abate da partida com mais frequência?",
                  "Qual campeão faz mais abates múltiplos?", "Quantos tripple kills existem no solo queue?", "Qual a maior sequência de abates sem morrer?"):
            self.recusa("solo", "U8-multikill", f, "sequência de abates ausente")
        for f in ("Em que minuto caiu a primeira torre, em média?", "Em que minuto acontece o primeiro dragão, em média?",
                  "Qual o minuto médio da primeira morte?", "Quanto tempo as partidas levam até o primeiro Barão?",
                  "Qual o minuto médio da quinta eliminação do jogo?", "Em que minuto os jogos costumam virar no ouro?"):
            self.recusa("solo", "U9-timeline", f, "momento de eventos ausente")

    def fechar(self):
        existentes = _perguntas_existentes()
        vistos, finais = set(), []
        for it in self.itens:
            k = _norm(it["pergunta"])
            if k in existentes or k in vistos:
                self.descartes["duplicada"] = self.descartes.get("duplicada", 0) + 1
                continue
            vistos.add(k)
            finais.append(it)
        # cota: ~90% respondíveis, ~10% sem resposta; embaralha com a semente e fixa em ALVO
        resp = [i for i in finais if not i["recusa_esperada"]]
        nao = [i for i in finais if i["recusa_esperada"]]
        self.rng.shuffle(resp)
        self.rng.shuffle(nao)
        n_nao = min(len(nao), round(ALVO * 0.11))
        escolhidos = resp[: ALVO - n_nao] + nao[:n_nao]
        self.rng.shuffle(escolhidos)
        for i, it in enumerate(escolhidos):
            it["id"] = PRIMEIRO_NUMERO + i
        return escolhidos


def main():
    g = Gerador()
    g.carregar()
    g.solo()
    g.competitivo()
    g.sem_resposta()
    itens = g.fechar()
    SAIDA_JSON.write_text(json.dumps({"semente": SEMENTE, "total": len(itens), "itens": itens},
                                     ensure_ascii=False, indent=1), encoding="utf-8")
    SAIDA_TXT.write_text("\n".join(f"{i['id']}. {i['pergunta']}" for i in itens) + "\n", encoding="utf-8")
    por_fam = {}
    for i in itens:
        por_fam[i["familia"]] = por_fam.get(i["familia"], 0) + 1
    print("total:", len(itens), "| recusa esperada:", sum(i["recusa_esperada"] for i in itens))
    print("por base:", {b: sum(1 for i in itens if i["base"] == b) for b in ("solo", "competitivo")})
    print("descartes:", g.descartes)
    for f, n in sorted(por_fam.items()):
        print(f"  {f}: {n}")


if __name__ == "__main__":
    main()
