"""API da plataforma (FastAPI, conforme seção 4.8 do TCC).

Endpoints: estatísticas para os dashboards (campeões, durações, lados,
gold diff aos 15), consulta em linguagem natural e predição de vitória
(modelo exportado por src/models/export_model.py).

Uso:  uvicorn src.api.main:app --reload
"""
import json
import os

import anthropic
import joblib
import pandas as pd
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.db import get_conn
from src.features.build_features import CUTOFFS, features_from_timeline
from src.nlq.nl_to_sql import SqlExecutionError, ask, explain_result

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
MODEL_PATH = "data/model.joblib"
MODELS_PHASES_PATH = "data/models_phases.joblib"
FEATURES_CSV = "data/features.csv"
ITEMS_PATH = "data/items.json"
POSITIONS = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

app = FastAPI(title="Bellestraiko", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # dev server do Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

# gráficos SHAP/calibração para a página de explicabilidade
if os.path.isdir("reports"):
    app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# modelos por fase (corte de tempo) carregados no startup, se exportados;
# fallback para o modelo único antigo (corte de 15) se só ele existir
if os.path.exists(MODELS_PHASES_PATH):
    _models: dict[int, object] = joblib.load(MODELS_PHASES_PATH)
elif os.path.exists(MODEL_PATH):
    _models = {15: joblib.load(MODEL_PATH)}
else:
    _models = {}
_explainers: dict[int, object] = {}
if _models:
    import shap

    _explainers = {cutoff: shap.TreeExplainer(m) for cutoff, m in _models.items()}


def _model_for_minute(minute: int):
    """Modelo do maior corte <= minuto (ou o menor corte disponível)."""
    eligible = [c for c in _models if c <= minute]
    cutoff = max(eligible) if eligible else min(_models)
    return cutoff, _models[cutoff]

# catálogo de itens (Data Dragon, gerado junto com o ETL de itens — ver
# docs/scripts.md, seção load_items). "Finalizado": nada constrói a partir
# dele, comprável, custo >= 1100, não consumível/trinket, válido no mapa 11.
_items: dict[str, dict] = {}
if os.path.exists(ITEMS_PATH):
    with open(ITEMS_PATH, encoding="utf-8") as f:
        _items = json.load(f)
_completed_item_ids = [
    int(iid)
    for iid, it in _items.items()
    if not it.get("into")
    and it.get("purchasable")
    and it.get("total_gold", 0) >= 1100
    and not ({"Consumable", "Trinket"} & set(it.get("tags", [])))
    and it.get("maps", {}).get("11")
]

# cache do features.csv para o gráfico gold diff aos 15 (recarrega se o
# arquivo for regenerado pelo build_features)
_features_cache: tuple[float, pd.DataFrame] | None = None


def _load_features() -> pd.DataFrame | None:
    global _features_cache
    if not os.path.exists(FEATURES_CSV):
        return None
    mtime = os.path.getmtime(FEATURES_CSV)
    if _features_cache is None or _features_cache[0] != mtime:
        _features_cache = (mtime, pd.read_csv(FEATURES_CSV))
    return _features_cache[1]


def _external_call_error(exc: Exception) -> HTTPException:
    """Converte falhas de infraestrutura (Claude API, banco) em uma
    resposta JSON com detail claro — nunca deixa a exceção propagar como
    um 500 sem corpo, para o front distinguir de erros de validação."""
    if isinstance(exc, anthropic.AuthenticationError):
        return HTTPException(
            status_code=502,
            detail="Chave da API Anthropic inválida ou ausente — verifique ANTHROPIC_API_KEY no .env.",
        )
    if isinstance(exc, anthropic.APIError):
        return HTTPException(status_code=502, detail=f"Erro ao consultar o serviço de IA: {exc}")
    if isinstance(exc, psycopg2.OperationalError):
        return HTTPException(status_code=503, detail="Não foi possível conectar ao banco de dados.")
    if isinstance(exc, psycopg2.Error):
        return HTTPException(
            status_code=422,
            detail="A consulta gerada não pôde ser executada — tente reformular a pergunta.",
        )
    return HTTPException(status_code=500, detail=f"Erro interno inesperado: {exc}")


class HistoryTurn(BaseModel):
    question: str
    sql: str


class Question(BaseModel):
    question: str
    history: list[HistoryTurn] = []


class ExplainRequest(BaseModel):
    question: str
    sql: str
    columns: list[str]
    rows: list[list]


class MatchState(BaseModel):
    """Estado da partida em um corte de tempo (diffs azul - vermelho)."""
    gold_diff: float
    xp_diff: float
    kill_diff: float
    tower_diff: float
    dragon_diff: float
    minute: int = 15  # corte: 10 (rotas), 15, 20 (mid), 25 (late)


class Composition(BaseModel):
    """Times por posição: {"TOP": "Jayce", "JUNGLE": "LeeSin", ...}.

    blue_players/red_players (opcional): {"TOP": "<puuid>", ...} — quem
    joga cada posição, usado para ajustar a estimativa pelo desempenho
    do jogador NAQUELE campeão (com shrinkage, ver compose()).

    state (opcional) simula um momento da partida: minuto + diffs de
    ouro/XP/abates/torres/dragões — combinado com a composição via
    modelo ML da fase correspondente."""
    blue: dict[str, str] = {}
    red: dict[str, str] = {}
    blue_players: dict[str, str] = {}
    red_players: dict[str, str] = {}
    state: MatchState | None = None


# jogos "equivalentes" do prior na shrinkage jogador×campeão — quanto
# maior, mais jogos o jogador precisa para se afastar da taxa do
# campeão (evita que 5 jogos 5/5 pareçam 100% de win rate)
PLAYER_SHRINKAGE_K = 15


# ---------------- estatísticas ----------------

@app.get("/stats/overview")
def overview():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM matches")
        n_matches = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT puuid) FROM participants")
        n_players = cur.fetchone()[0]
        cur.execute("SELECT AVG(game_duration_s)/60.0 FROM matches")
        avg_min = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT game_version) FROM matches")
        n_patches = cur.fetchone()[0]
        cur.execute("SELECT AVG(win::int) FROM teams WHERE team_id = 100")
        blue_wr = cur.fetchone()[0]
        cur.execute(
            """SELECT AVG(k) FROM
               (SELECT SUM(kills) AS k FROM participants GROUP BY match_id) t"""
        )
        avg_kills = cur.fetchone()[0]
        cur.execute(
            "SELECT AVG((game_duration_s >= 1500)::int) FROM matches"
        )
        late_rate = cur.fetchone()[0]
    return {
        "matches": n_matches,
        "players": n_players,
        "avg_duration_min": round(float(avg_min or 0), 1),
        "patches": n_patches,
        "blue_win_rate": round(float(blue_wr or 0), 4),
        "avg_kills": round(float(avg_kills or 0), 1),
        "late_game_rate": round(float(late_rate or 0), 4),
    }


@app.get("/stats/patches")
def patches():
    """Partidas por patch (cobertura do dataset ao longo das versões)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT split_part(game_version, '.', 1) || '.' || split_part(game_version, '.', 2) AS patch,
                      COUNT(*) AS matches, AVG(win::int) AS blue_wr
               FROM matches m JOIN teams t ON t.match_id = m.match_id AND t.team_id = 100
               GROUP BY patch ORDER BY MIN(m.game_creation)"""
        )
        rows = cur.fetchall()
    return [
        {"patch": r[0], "matches": r[1], "blue_win_rate": round(float(r[2]), 4)}
        for r in rows
    ]


@app.get("/stats/regions")
def regions():
    """Cobertura e viés de lado por região/plataforma (planejamento v2,
    sprint 5) — a mesma pergunta do viés de lado BR, agora comparável
    entre plataformas: é um achado de solo queue de elo alto em geral,
    ou específico do BR? Cada linha usa o time vermelho (mesmo ângulo
    do /stats/highlights): win rate vermelho > 50% = vermelho favorecido."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT m.platform_id, COUNT(*) AS matches,
                      AVG(t.win::int) AS red_win_rate,
                      AVG(m.game_duration_s) / 60.0 AS avg_duration_min
               FROM matches m JOIN teams t ON t.match_id = m.match_id AND t.team_id = 200
               GROUP BY m.platform_id ORDER BY matches DESC"""
        )
        rows = cur.fetchall()
    return [
        {
            "platform": r[0],
            "matches": r[1],
            "red_win_rate": round(float(r[2]), 4),
            "avg_duration_min": round(float(r[3]), 1),
        }
        for r in rows
    ]


CHAMPION_SORTS = {
    "games": "games",
    "win_rate": "win_rate",
    "pick_rate": "games",  # pick rate é proporcional a games
    "ban_rate": "ban_rate",
    "kda": "kda",
    "avg_cs": "avg_cs",
    "avg_gold": "avg_gold",
    "avg_dmg": "avg_dmg",
}


@app.get("/stats/champions")
def champions(
    min_games: int = 20,
    limit: int = 200,
    sort: str = "games",
    role: str = "",
    search: str = "",
):
    order_col = CHAMPION_SORTS.get(sort)
    if order_col is None:
        raise HTTPException(status_code=400, detail=f"sort deve ser um de: {list(CHAMPION_SORTS)}")
    role = role.upper()
    if role and role not in POSITIONS:
        raise HTTPException(status_code=400, detail=f"role deve ser um de: {POSITIONS}")

    role_filter = "AND team_position = %(role)s" if role else ""
    search_filter = "AND champion_name ILIKE %(search)s" if search else ""
    sql = f"""
        WITH total AS (SELECT COUNT(*)::float AS n FROM matches),
        stats AS (
            SELECT champion_name,
                   MIN(champion_id) AS champion_id,
                   COUNT(*) AS games,
                   AVG(win::int) AS win_rate,
                   (SUM(kills) + SUM(assists))::float / NULLIF(SUM(deaths), 0) AS kda,
                   AVG(cs_total) AS avg_cs,
                   AVG(gold_earned) AS avg_gold,
                   AVG(dmg_to_champions) AS avg_dmg,
                   MODE() WITHIN GROUP (ORDER BY team_position) AS main_position
            FROM participants
            WHERE team_position != '' {role_filter} {search_filter}
            GROUP BY champion_name
            HAVING COUNT(*) >= %(min_games)s
        ),
        ban_counts AS (
            SELECT p.champion_name, COUNT(DISTINCT b.match_id) AS banned
            FROM (SELECT DISTINCT champion_id, champion_name FROM participants) p
            JOIN bans b ON b.champion_id = p.champion_id
            GROUP BY p.champion_name
        )
        SELECT s.champion_name, s.champion_id, s.games, s.win_rate,
               s.games / t.n AS pick_rate,
               COALESCE(bc.banned, 0) / t.n AS ban_rate,
               s.kda, s.avg_cs, s.avg_gold, s.avg_dmg, s.main_position
        FROM stats s
        CROSS JOIN total t
        LEFT JOIN ban_counts bc ON bc.champion_name = s.champion_name
        ORDER BY {order_col} DESC NULLS LAST
        LIMIT %(limit)s
    """
    params = {"min_games": min_games, "limit": limit, "role": role, "search": f"%{search}%"}
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [
        {
            "champion": r[0],
            "champion_id": r[1],
            "games": r[2],
            "win_rate": round(float(r[3]), 4),
            "pick_rate": round(float(r[4]), 4),
            "ban_rate": round(float(r[5]), 4),
            "kda": round(float(r[6]), 2) if r[6] is not None else None,
            "avg_cs": round(float(r[7]), 1),
            "avg_gold": round(float(r[8])),
            "avg_dmg": round(float(r[9])),
            "main_position": r[10],
        }
        for r in rows
    ]


@app.get("/stats/champion/{champion_name}")
def champion_detail(champion_name: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT MIN(champion_id), COUNT(*), AVG(win::int),
                      (SUM(kills)+SUM(assists))::float / NULLIF(SUM(deaths),0),
                      AVG(cs_total), AVG(gold_earned), AVG(dmg_to_champions),
                      (SELECT COUNT(*)::float FROM matches)
               FROM participants WHERE champion_name = %s""",
            (champion_name,),
        )
        r = cur.fetchone()
        if not r or r[1] == 0:
            raise HTTPException(status_code=404, detail=f"Campeão '{champion_name}' não encontrado.")
        cur.execute(
            """SELECT COUNT(DISTINCT b.match_id) FROM bans b
               WHERE b.champion_id = %s""",
            (r[0],),
        )
        banned = cur.fetchone()[0]

        cur.execute(
            """SELECT team_position, COUNT(*), AVG(win::int),
                      (SUM(kills)+SUM(assists))::float / NULLIF(SUM(deaths),0)
               FROM participants
               WHERE champion_name = %s AND team_position != ''
               GROUP BY team_position ORDER BY COUNT(*) DESC""",
            (champion_name,),
        )
        positions = [
            {"position": p[0], "games": p[1], "win_rate": round(float(p[2]), 4),
             "kda": round(float(p[3]), 2) if p[3] is not None else None}
            for p in cur.fetchall()
        ]

        cur.execute(
            """SELECT p2.champion_name, MIN(p2.champion_id), COUNT(*), AVG(p1.win::int)
               FROM participants p1
               JOIN participants p2 ON p2.match_id = p1.match_id
                AND p2.team_id != p1.team_id AND p2.team_position = p1.team_position
               WHERE p1.champion_name = %s AND p1.team_position != ''
               GROUP BY p2.champion_name
               HAVING COUNT(*) >= 15
               ORDER BY AVG(p1.win::int) DESC""",
            (champion_name,),
        )
        matchups = [
            {"opponent": m[0], "opponent_id": m[1], "games": m[2], "win_rate": round(float(m[3]), 4)}
            for m in cur.fetchall()
        ]

        cur.execute(
            """SELECT p.match_id, m.game_creation, m.game_duration_s, m.game_version,
                      p.team_position, p.kills, p.deaths, p.assists, p.win
               FROM participants p JOIN matches m USING (match_id)
               WHERE p.champion_name = %s
               ORDER BY m.game_creation DESC LIMIT 10""",
            (champion_name,),
        )
        recent = [
            {
                "match_id": g[0],
                "date": g[1].isoformat(),
                "duration_min": round(g[2] / 60.0, 1),
                "patch": ".".join(g[3].split(".")[:2]) if g[3] else None,
                "position": g[4],
                "kills": g[5], "deaths": g[6], "assists": g[7],
                "win": g[8],
            }
            for g in cur.fetchall()
        ]

    total = r[7]
    return {
        "champion": champion_name,
        "champion_id": r[0],
        "games": r[1],
        "win_rate": round(float(r[2]), 4),
        "pick_rate": round(r[1] / total, 4),
        "ban_rate": round(banned / total, 4),
        "kda": round(float(r[3]), 2) if r[3] is not None else None,
        "avg_cs": round(float(r[4]), 1),
        "avg_gold": round(float(r[5])),
        "avg_dmg": round(float(r[6])),
        "positions": positions,
        "matchups": matchups,
        "recent_games": recent,
    }


@app.get("/stats/champion/{champion_name}/items")
def champion_items(champion_name: str):
    """Itens finalizados mais construídos pelo campeão: em quantos jogos o
    item foi comprado, win rate nesses jogos e minuto médio da compra
    (item_events, ETL de src/etl/load_items.py)."""
    if not _completed_item_ids:
        raise HTTPException(
            status_code=503,
            detail="Catálogo de itens não carregado — gere data/items.json (ver docs/scripts.md, load_items).",
        )
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM participants WHERE champion_name = %s", (champion_name,)
        )
        champ_games = cur.fetchone()[0]
        if champ_games == 0:
            raise HTTPException(status_code=404, detail=f"Campeão '{champion_name}' não encontrado.")
        # filtra pelo campeão ANTES de agregar (item_events tem milhões de
        # linhas); primeira compra por (partida, item) para não contar
        # recompra após venda como dois jogos
        cur.execute(
            """WITH champ AS (
                   SELECT match_id, puuid, win FROM participants WHERE champion_name = %s
               ),
               first_buys AS (
                   SELECT ie.match_id, ie.puuid, ie.item_id, MIN(ie.ts_ms) AS ts_ms
                   FROM item_events ie
                   JOIN champ c ON c.match_id = ie.match_id AND c.puuid = ie.puuid
                   WHERE ie.action = 'BUY' AND ie.item_id = ANY(%s)
                   GROUP BY ie.match_id, ie.puuid, ie.item_id
               )
               SELECT fb.item_id, COUNT(*) AS games, AVG(c.win::int) AS win_rate,
                      AVG(fb.ts_ms) / 60000.0 AS avg_minute
               FROM first_buys fb
               JOIN champ c ON c.match_id = fb.match_id AND c.puuid = fb.puuid
               GROUP BY fb.item_id
               HAVING COUNT(*) >= 20
               ORDER BY COUNT(*) DESC
               LIMIT 12""",
            (champion_name, _completed_item_ids),
        )
        rows = cur.fetchall()
    return {
        "champion": champion_name,
        "games": champ_games,
        "items": [
            {
                "item_id": r[0],
                "name": _items.get(str(r[0]), {}).get("name", f"Item {r[0]}"),
                "games": r[1],
                "pick_share": round(r[1] / champ_games, 4),
                "win_rate": round(float(r[2]), 4),
                "avg_minute": round(float(r[3]), 1),
            }
            for r in rows
        ],
    }


@app.get("/stats/champion/{champion_name}/pro")
def champion_pro(champion_name: str, year: int | None = None):
    """Presença e desempenho do campeão no COMPETITIVO (pro_players):
    jogos, win rate, presença sobre os jogos do ano e quebra por liga.
    O nome interno da Riot é casado com o nome de exibição do Oracle's
    Elixir pela mesma normalização do /stats/pro/champions."""
    norm = champion_name.lower()
    with get_conn() as conn, conn.cursor() as cur:
        year = _pro_year(cur, year)
        cur.execute(
            """WITH picks AS (
                   SELECT pg.league, pp.win
                   FROM pro_players pp
                   JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
                   WHERE pg.year = %s
                     AND lower(regexp_replace(
                             CASE pp.champion
                                 WHEN 'Wukong' THEN 'MonkeyKing'
                                 WHEN 'Renata Glasc' THEN 'Renata'
                                 WHEN 'Nunu & Willump' THEN 'Nunu'
                                 ELSE pp.champion
                             END, '[^a-zA-Z]', '', 'g')) = %s
               ),
               total AS (
                   SELECT COUNT(DISTINCT game_id)::float AS n
                   FROM pro_games WHERE year = %s
               )
               SELECT (SELECT COUNT(*) FROM picks),
                      (SELECT AVG(win::int) FROM picks),
                      (SELECT n FROM total)""",
            (year, norm, year),
        )
        games, wr, total = cur.fetchone()
        leagues = []
        if games:
            cur.execute(
                """SELECT pg.league, COUNT(*) AS games, AVG(pp.win::int) AS wr
                   FROM pro_players pp
                   JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
                   WHERE pg.year = %s
                     AND lower(regexp_replace(
                             CASE pp.champion
                                 WHEN 'Wukong' THEN 'MonkeyKing'
                                 WHEN 'Renata Glasc' THEN 'Renata'
                                 WHEN 'Nunu & Willump' THEN 'Nunu'
                                 ELSE pp.champion
                             END, '[^a-zA-Z]', '', 'g')) = %s
                   GROUP BY pg.league ORDER BY games DESC LIMIT 6""",
                (year, norm),
            )
            leagues = [
                {"league": r[0], "games": r[1], "win_rate": round(float(r[2]), 4)}
                for r in cur.fetchall()
            ]
    return {
        "champion": champion_name,
        "year": year,
        "games": games,
        "win_rate": round(float(wr), 4) if wr is not None else None,
        "presence": round(games / total, 4) if total else 0,
        "leagues": leagues,
    }


@app.get("/stats/players/search")
def players_search(q: str):
    """Busca de jogadores por nome, nos DOIS datasets: solo queue
    (players.game_name, via Riot ID) e competitivo (pro_players).
    Alimenta a busca unificada da Home."""
    q = q.strip()
    if len(q) < 3:
        return {"solo": [], "pro": []}
    like = f"%{q}%"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT p.puuid, p.game_name, p.tag_line, p.tier,
                      COUNT(pt.match_id) AS games, AVG(pt.win::int) AS wr
               FROM players p
               JOIN participants pt ON pt.puuid = p.puuid
               WHERE p.game_name ILIKE %s
               GROUP BY p.puuid, p.game_name, p.tag_line, p.tier
               ORDER BY games DESC LIMIT 5""",
            (like,),
        )
        solo = [
            {
                "puuid": r[0], "name": r[1], "tag": r[2], "tier": r[3],
                "games": r[4], "win_rate": round(float(r[5]), 4),
            }
            for r in cur.fetchall()
        ]
        cur.execute(
            """SELECT pp.player_name, COUNT(*) AS games,
                      (ARRAY_AGG(pp.team_name ORDER BY pg.game_date DESC))[1] AS team
               FROM pro_players pp
               JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
               WHERE pp.player_name ILIKE %s
               GROUP BY pp.player_name ORDER BY games DESC LIMIT 5""",
            (like,),
        )
        pro = [{"name": r[0], "games": r[1], "team": r[2]} for r in cur.fetchall()]
    return {"solo": solo, "pro": pro}


@app.get("/stats/player/{puuid}")
def player_profile(puuid: str):
    """Perfil de um jogador de solo queue: identidade (Riot ID/tier),
    totais, pool de campeões e partidas recentes."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT game_name, tag_line, tier, division, league_points
               FROM players WHERE puuid = %s""",
            (puuid,),
        )
        ident = cur.fetchone()
        cur.execute(
            """SELECT COUNT(*), AVG(win::int),
                      MODE() WITHIN GROUP (ORDER BY team_position)
               FROM participants WHERE puuid = %s AND team_position != ''""",
            (puuid,),
        )
        games, wr, main_pos = cur.fetchone()
        if not games:
            raise HTTPException(status_code=404, detail="Jogador sem partidas no dataset.")
        cur.execute(
            """SELECT champion_name, MIN(champion_id), COUNT(*), AVG(win::int),
                      (SUM(kills)+SUM(assists))::float / NULLIF(SUM(deaths),0)
               FROM participants WHERE puuid = %s
               GROUP BY champion_name ORDER BY COUNT(*) DESC LIMIT 10""",
            (puuid,),
        )
        pool = [
            {
                "champion": r[0], "champion_id": r[1], "games": r[2],
                "win_rate": round(float(r[3]), 4),
                "kda": round(float(r[4]), 2) if r[4] is not None else None,
            }
            for r in cur.fetchall()
        ]
        cur.execute(
            """SELECT p.match_id, m.game_creation, m.game_duration_s,
                      p.champion_name, p.champion_id, p.team_position,
                      p.kills, p.deaths, p.assists, p.win
               FROM participants p JOIN matches m USING (match_id)
               WHERE p.puuid = %s
               ORDER BY m.game_creation DESC LIMIT 10""",
            (puuid,),
        )
        recent = [
            {
                "match_id": r[0], "date": r[1].isoformat(),
                "duration_min": round(r[2] / 60.0, 1),
                "champion": r[3], "champion_id": r[4], "position": r[5],
                "kills": r[6], "deaths": r[7], "assists": r[8], "win": r[9],
            }
            for r in cur.fetchall()
        ]
    return {
        "puuid": puuid,
        "name": ident[0] if ident else None,
        "tag": ident[1] if ident else None,
        "tier": ident[2] if ident else None,
        "division": ident[3] if ident else None,
        "league_points": ident[4] if ident else None,
        "games": games,
        "win_rate": round(float(wr), 4),
        "main_position": main_pos,
        "champion_pool": pool,
        "recent_games": recent,
    }


@app.get("/stats/pro/player/{player_name}")
def pro_player_profile(player_name: str):
    """Perfil de um jogador PROFISSIONAL: temporadas (ano/time/liga),
    pool de campeões (com ícone quando o nome casa com o solo queue) e
    totais. Nome casado case-insensitive (padrão do Oracle's Elixir)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT COUNT(*), AVG(pp.win::int),
                      MODE() WITHIN GROUP (ORDER BY pp.position)
               FROM pro_players pp
               WHERE lower(pp.player_name) = lower(%s)""",
            (player_name,),
        )
        games, wr, main_pos = cur.fetchone()
        if not games:
            raise HTTPException(status_code=404, detail=f"Jogador '{player_name}' não encontrado no competitivo.")
        cur.execute(
            """SELECT pg.year, pp.team_name, pg.league, COUNT(*) AS games,
                      AVG(pp.win::int) AS wr
               FROM pro_players pp
               JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
               WHERE lower(pp.player_name) = lower(%s)
               GROUP BY pg.year, pp.team_name, pg.league
               ORDER BY pg.year DESC, games DESC LIMIT 15""",
            (player_name,),
        )
        seasons = [
            {
                "year": r[0], "team": r[1], "league": r[2],
                "games": r[3], "win_rate": round(float(r[4]), 4),
            }
            for r in cur.fetchall()
        ]
        cur.execute(
            """WITH pool AS (
                   SELECT pp.champion, COUNT(*) AS games, AVG(pp.win::int) AS wr,
                          lower(regexp_replace(
                              CASE pp.champion
                                  WHEN 'Wukong' THEN 'MonkeyKing'
                                  WHEN 'Renata Glasc' THEN 'Renata'
                                  WHEN 'Nunu & Willump' THEN 'Nunu'
                                  ELSE pp.champion
                              END, '[^a-zA-Z]', '', 'g')) AS norm
                   FROM pro_players pp
                   WHERE lower(pp.player_name) = lower(%s)
                   GROUP BY pp.champion
               ),
               solo AS (
                   SELECT lower(champion_name) AS norm, MIN(champion_id) AS champion_id
                   FROM participants GROUP BY lower(champion_name)
               )
               SELECT p.champion, p.games, p.wr, s.champion_id
               FROM pool p LEFT JOIN solo s ON s.norm = p.norm
               ORDER BY p.games DESC LIMIT 12""",
            (player_name,),
        )
        pool = [
            {
                "champion": r[0], "games": r[1],
                "win_rate": round(float(r[2]), 4), "champion_id": r[3],
            }
            for r in cur.fetchall()
        ]
    return {
        "name": player_name,
        "games": games,
        "win_rate": round(float(wr), 4),
        "main_position": main_pos,
        "current_team": seasons[0]["team"] if seasons else None,
        "seasons": seasons,
        "champion_pool": pool,
    }


@app.get("/stats/objectives")
def objectives():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT win, AVG(dragons) AS dragons, AVG(barons) AS barons,
                      AVG(towers) AS towers, AVG(heralds) AS heralds
               FROM teams GROUP BY win ORDER BY win"""
        )
        rows = cur.fetchall()
    return [
        {
            "win": r[0],
            "dragons": round(float(r[1]), 2),
            "barons": round(float(r[2]), 2),
            "towers": round(float(r[3]), 2),
            "heralds": round(float(r[4]), 2),
        }
        for r in rows
    ]


@app.get("/stats/durations")
def durations():
    """Histograma de duração das partidas (faixas de 5 min)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT width_bucket(game_duration_s / 60.0, 15, 45, 6) AS bucket, COUNT(*)
               FROM matches GROUP BY bucket ORDER BY bucket"""
        )
        rows = dict(cur.fetchall())
    labels = ["< 15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "> 45"]
    return [{"range": labels[b], "matches": rows.get(b, 0)} for b in range(8)]


@app.get("/stats/gold15")
def gold15():
    """Win rate do time azul por faixa de diferença de ouro aos 15 min
    (a métrica-assinatura do modelo, calculada das timelines reais)."""
    df = _load_features()
    if df is None:
        raise HTTPException(
            status_code=503,
            detail="Features não geradas — rode: python -m src.features.build_features",
        )
    bins = list(range(-8000, 8001, 2000))
    cut = pd.cut(df["gold_diff"].clip(-7999, 7999), bins=bins)
    grouped = df.groupby(cut, observed=True)["blue_win"]
    out = []
    for interval, series in grouped:
        out.append(
            {
                "gold_diff_mid": int(interval.mid),
                "label": f"{int(interval.left/1000):+d}k a {int(interval.right/1000):+d}k",
                "blue_win_rate": round(float(series.mean()), 4),
                "matches": int(series.count()),
            }
        )
    return out


@app.get("/matches/recent")
def recent_matches(limit: int = 15):
    limit = max(1, min(limit, 50))
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT match_id, game_creation, game_duration_s, game_version
               FROM matches ORDER BY game_creation DESC LIMIT %s""",
            (limit,),
        )
        matches = cur.fetchall()
        ids = [m[0] for m in matches]
        cur.execute(
            """SELECT match_id, team_id, champion_name, champion_id, team_position,
                      kills, deaths, assists, win
               FROM participants WHERE match_id = ANY(%s)""",
            (ids,),
        )
        parts: dict[str, list] = {}
        for p in cur.fetchall():
            parts.setdefault(p[0], []).append(p)

    pos_order = {p: i for i, p in enumerate(POSITIONS)}
    out = []
    for mid, creation, duration, version in matches:
        players = sorted(
            parts.get(mid, []),
            key=lambda p: (p[1], pos_order.get(p[4], 9)),
        )
        out.append(
            {
                "match_id": mid,
                "date": creation.isoformat(),
                "duration_min": round(duration / 60.0, 1),
                "patch": ".".join(version.split(".")[:2]) if version else None,
                "blue_win": any(p[8] for p in players if p[1] == 100),
                "participants": [
                    {
                        "team_id": p[1],
                        "champion": p[2],
                        "champion_id": p[3],
                        "position": p[4],
                        "kills": p[5], "deaths": p[6], "assists": p[7],
                    }
                    for p in players
                ],
            }
        )
    return out


@app.get("/matches/{match_id}/analysis")
def match_analysis(match_id: str):
    """Análise completa de uma partida: curva de probabilidade de vitória
    minuto a minuto (modelos por fase), evolução do ouro e stats finais."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT game_creation, game_duration_s, game_version
               FROM matches WHERE match_id = %s""",
            (match_id,),
        )
        meta = cur.fetchone()
        if meta is None:
            raise HTTPException(status_code=404, detail=f"Partida '{match_id}' não encontrada.")
        cur.execute(
            """SELECT team_id, champion_name, champion_id, team_position, puuid,
                      kills, deaths, assists, gold_earned, cs_total, vision_score,
                      dmg_to_champions, win
               FROM participants WHERE match_id = %s""",
            (match_id,),
        )
        players = cur.fetchall()
        cur.execute(
            """SELECT team_id, win, barons, dragons, heralds, towers, inhibitors
               FROM teams WHERE match_id = %s ORDER BY team_id""",
            (match_id,),
        )
        teams = cur.fetchall()
        cur.execute("SELECT payload FROM raw_timelines WHERE match_id = %s", (match_id,))
        tl = cur.fetchone()

    prob_curve = []
    if tl is not None and _models:
        payload = tl[0]
        n_frames = len(payload.get("info", {}).get("frames", []))
        for minute in range(1, n_frames):
            feats = features_from_timeline(payload, minute)
            if feats is None:
                break
            cutoff, model = _model_for_minute(minute)
            X = pd.DataFrame([[feats[f] for f in FEATURES]], columns=FEATURES)
            prob_curve.append(
                {
                    "minute": minute,
                    "blue_win_probability": round(float(model.predict_proba(X)[0, 1]), 4),
                    "model_cutoff": cutoff,
                    # estado completo do minuto — semente do modo "e se" no
                    # front (editar o estado real e ver o delta via /predict)
                    **{f: feats[f] for f in FEATURES},
                }
            )

    pos_order = {p: i for i, p in enumerate(POSITIONS)}
    return {
        "match_id": match_id,
        "date": meta[0].isoformat(),
        "duration_min": round(meta[1] / 60.0, 1),
        "patch": ".".join(meta[2].split(".")[:2]) if meta[2] else None,
        "teams": [
            {
                "team_id": t[0], "win": t[1], "barons": t[2], "dragons": t[3],
                "heralds": t[4], "towers": t[5], "inhibitors": t[6],
            }
            for t in teams
        ],
        "participants": [
            {
                "team_id": p[0], "champion": p[1], "champion_id": p[2],
                "position": p[3],
                "kills": p[5], "deaths": p[6], "assists": p[7],
                "gold": p[8], "cs": p[9], "vision": p[10], "dmg": p[11],
                "win": p[12],
            }
            for p in sorted(players, key=lambda p: (p[0], pos_order.get(p[3], 9)))
        ],
        "prob_curve": prob_curve,
    }


@app.get("/matches/{match_id}/positions")
def match_positions(match_id: str):
    """Posições dos 10 jogadores minuto a minuto (participantFrames da
    timeline) + abates com local — base do mapa de calor da análise.

    Coordenadas no sistema do mapa 11 (Summoner's Rift): x e y crescem
    da base azul (canto inferior esquerdo) para a vermelha; o front
    normaliza pelos bounds e inverte o y para desenhar sobre a imagem."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT payload FROM raw_timelines WHERE match_id = %s", (match_id,))
        tl = cur.fetchone()
        if tl is None:
            raise HTTPException(
                status_code=404,
                detail=f"Sem timeline disponível para a partida '{match_id}'.",
            )
        cur.execute(
            """SELECT puuid, team_id, champion_name, champion_id
               FROM participants WHERE match_id = %s""",
            (match_id,),
        )
        by_puuid = {r[0]: (r[1], r[2], r[3]) for r in cur.fetchall()}

    info = tl[0].get("info", {})
    # participantId da timeline -> (team, campeão) via puuid
    id_map = {}
    for p in info.get("participants", []):
        meta = by_puuid.get(p.get("puuid"))
        if meta:
            id_map[p.get("participantId")] = meta

    # eventos de objetivo -> categoria da tabela teams
    monster_kind = {"DRAGON": "dragons", "BARON_NASHOR": "barons", "RIFTHERALD": "heralds"}
    building_kind = {"TOWER_BUILDING": "towers", "INHIBITOR_BUILDING": "inhibitors"}

    frames, kills, objectives = [], [], []
    for i, fr in enumerate(info.get("frames", [])):
        players = []
        for pf in fr.get("participantFrames", {}).values():
            pos, meta = pf.get("position"), id_map.get(pf.get("participantId"))
            if pos is None or meta is None:
                continue
            players.append(
                {
                    "team_id": meta[0], "champion": meta[1], "champion_id": meta[2],
                    "x": pos["x"], "y": pos["y"], "level": pf.get("level"),
                }
            )
        frames.append({"minute": i, "players": players})
        for e in fr.get("events", []):
            minute = e.get("timestamp", 0) // 60000
            if e.get("type") == "CHAMPION_KILL" and "position" in e:
                victim = id_map.get(e.get("victimId"))
                # killerId 0 = execução (torre/monstro); credita ao time oposto ao da vítima
                killer = id_map.get(e.get("killerId"))
                team = killer[0] if killer else (300 - victim[0] if victim else None)
                kills.append(
                    {
                        "minute": minute,
                        "x": e["position"]["x"], "y": e["position"]["y"],
                        "killer_team": team,
                    }
                )
            elif e.get("type") == "ELITE_MONSTER_KILL":
                kind = monster_kind.get(e.get("monsterType"))
                # killerTeamId 300 = execução neutra (raro); fica fora da contagem
                if kind and e.get("killerTeamId") in (100, 200):
                    objectives.append(
                        {"minute": minute, "kind": kind, "team_id": e["killerTeamId"]}
                    )
            elif e.get("type") == "BUILDING_KILL":
                kind = building_kind.get(e.get("buildingType"))
                # teamId aqui é o dono da construção destruída — pontua o oposto
                if kind and e.get("teamId") in (100, 200):
                    objectives.append(
                        {"minute": minute, "kind": kind, "team_id": 300 - e["teamId"]}
                    )

    return {
        "match_id": match_id,
        "frames": frames,
        "kills": kills,
        "objectives": objectives,
        # bounds oficiais do mapa 11 (min -120, max 14870/14980)
        "bounds": {"min": -120, "max_x": 14870, "max_y": 14980},
    }


@app.get("/stats/highlights")
def highlights():
    """Destaques para a página inicial — cada um com os números que
    fundamentam o insight (o 'porquê' é montado no front)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT p.puuid, COALESCE(p.game_name, ''), COALESCE(p.tag_line, ''),
                      p.tier, COUNT(*) AS games, AVG(pt.win::int) AS wr
               FROM players p JOIN participants pt ON pt.puuid = p.puuid
               GROUP BY p.puuid, p.game_name, p.tag_line, p.tier
               HAVING COUNT(*) >= 20 ORDER BY AVG(pt.win::int) DESC LIMIT 1"""
        )
        bp = cur.fetchone()
        cur.execute(
            """SELECT champion_name, MIN(champion_id), COUNT(*), AVG(win::int)
               FROM participants GROUP BY champion_name
               HAVING COUNT(*) >= 200 ORDER BY AVG(win::int) DESC LIMIT 1"""
        )
        bc = cur.fetchone()
        cur.execute(
            """SELECT p1.champion_name, MIN(p1.champion_id) AS c1_id,
                      p2.champion_name, MIN(p2.champion_id) AS c2_id,
                      COUNT(*), AVG(p1.win::int) AS wr
               FROM participants p1
               JOIN participants p2 ON p2.match_id = p1.match_id
                AND p2.team_id != p1.team_id AND p2.team_position = p1.team_position
               WHERE p1.team_position != ''
               GROUP BY p1.champion_name, p2.champion_name
               HAVING COUNT(*) >= 30 ORDER BY AVG(p1.win::int) DESC LIMIT 1"""
        )
        mu = cur.fetchone()
        cur.execute(
            """SELECT p.champion_name, MIN(p.champion_id),
                      COUNT(DISTINCT b.match_id)::float / (SELECT COUNT(*) FROM matches)
               FROM bans b
               JOIN (SELECT DISTINCT champion_id, champion_name FROM participants) p
                 ON p.champion_id = b.champion_id
               GROUP BY p.champion_name ORDER BY COUNT(DISTINCT b.match_id) DESC LIMIT 1"""
        )
        ban = cur.fetchone()
        cur.execute("SELECT AVG(win::int) FROM teams WHERE team_id = 200")
        red_wr = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM matches")
        total = cur.fetchone()[0]

    return {
        "total_matches": total,
        "best_player": {
            "puuid": bp[0],
            "name": bp[1] or None,
            "tag": bp[2] or None,
            "tier": bp[3],
            "games": bp[4],
            "win_rate": round(float(bp[5]), 4),
        } if bp else None,
        "best_champion": {
            "champion": bc[0],
            "champion_id": bc[1],
            "games": bc[2],
            "win_rate": round(float(bc[3]), 4),
        } if bc else None,
        "most_lopsided_matchup": {
            "champion": mu[0],
            "champion_id": mu[1],
            "opponent": mu[2],
            "opponent_id": mu[3],
            "games": mu[4],
            "win_rate": round(float(mu[5]), 4),
        } if mu else None,
        "most_banned": {
            "champion": ban[0],
            "champion_id": ban[1],
            "ban_rate": round(float(ban[2]), 4),
        } if ban else None,
        "red_side_win_rate": round(float(red_wr), 4),
    }


@app.post("/compose")
def compose(comp: Composition):
    """Análise de composição (montar time): matchups por lane, sinergias
    de dupla e uma estimativa heurística de vitória — baseada em win
    rates históricos, distinta do modelo ML de estado de partida."""
    import math

    logit = lambda p: math.log(p / (1 - p))

    positions = [p for p in POSITIONS if p in comp.blue and p in comp.red]
    if not positions:
        raise HTTPException(
            status_code=400,
            detail="Preencha ao menos uma posição nos dois times (TOP/JUNGLE/MIDDLE/BOTTOM/UTILITY).",
        )

    # um campeão só pode ser escolhido uma vez na partida (regra do jogo)
    picks = list(comp.blue.values()) + list(comp.red.values())
    dup = sorted({c for c in picks if picks.count(c) > 1})
    if dup:
        raise HTTPException(
            status_code=400,
            detail=f"Campeão repetido na partida: {', '.join(dup)} — cada campeão só pode ser escolhido uma vez.",
        )

    with get_conn() as conn, conn.cursor() as cur:
        # ids + win rate geral dos campeões envolvidos (cache local)
        champs = set(comp.blue.values()) | set(comp.red.values())
        cur.execute(
            """SELECT champion_name, MIN(champion_id), COUNT(*), AVG(win::int)
               FROM participants WHERE champion_name = ANY(%s)
               GROUP BY champion_name""",
            (list(champs),),
        )
        profile = {r[0]: {"id": r[1], "games": r[2], "wr": float(r[3])} for r in cur.fetchall()}
        missing = champs - set(profile)
        if missing:
            raise HTTPException(status_code=404, detail=f"Campeões não encontrados: {sorted(missing)}")

        def player_effect(puuid: str | None, champion: str) -> dict | None:
            """Ajuste em log-odds do desempenho do jogador NAQUELE campeão,
            com shrinkage bayesiano para a taxa geral do campeão — um
            jogador com poucos jogos fica perto de 0 (efeito neutro); com
            muitos jogos, o efeito se aproxima da diferença real observada.
            shrunk = (jogos*wr_jogador + k*wr_campeao) / (jogos + k)."""
            if not puuid:
                return None
            cur.execute(
                """SELECT COUNT(*), AVG(win::int) FROM participants
                   WHERE puuid = %s AND champion_name = %s""",
                (puuid, champion),
            )
            games, wr = cur.fetchone()
            cur.execute("SELECT game_name, tag_line FROM players WHERE puuid = %s", (puuid,))
            ident = cur.fetchone()
            champ_wr = profile[champion]["wr"]
            games = games or 0
            player_wr = float(wr) if wr is not None else champ_wr
            shrunk = (games * player_wr + PLAYER_SHRINKAGE_K * champ_wr) / (games + PLAYER_SHRINKAGE_K)
            shrunk = min(0.95, max(0.05, shrunk))
            logit_delta = logit(shrunk) - logit(champ_wr)
            return {
                "name": f"{ident[0]}#{ident[1]}" if ident and ident[0] else puuid[:8] + "…",
                "games_on_champion": games,
                "raw_win_rate": round(player_wr, 4) if games > 0 else None,
                "shrunk_win_rate": round(shrunk, 4),
                "logit_delta": logit_delta,
            }

        lanes = []
        for pos in positions:
            b, r = comp.blue[pos], comp.red[pos]
            cur.execute(
                """SELECT COUNT(*), AVG(p1.win::int)
                   FROM participants p1
                   JOIN participants p2 ON p2.match_id = p1.match_id
                    AND p2.team_id != p1.team_id AND p2.team_position = p1.team_position
                   WHERE p1.champion_name = %s AND p2.champion_name = %s
                     AND p1.team_position = %s""",
                (b, r, pos),
            )
            games, wr = cur.fetchone()
            if games >= 10 and wr is not None:
                lane_wr, source = float(wr), "matchup"
            else:
                # amostra pequena: cai para a diferença dos perfis gerais
                lane_wr = min(0.95, max(0.05, 0.5 + (profile[b]["wr"] - profile[r]["wr"]) / 2))
                source = "perfil"

            # ajuste opcional de jogador: soma o efeito (em log-odds) de
            # quem joga cada lado — jogador azul melhor empurra a favor do
            # azul, jogador vermelho melhor empurra contra
            blue_player = player_effect(comp.blue_players.get(pos), b)
            red_player = player_effect(comp.red_players.get(pos), r)
            player_adj = (blue_player["logit_delta"] if blue_player else 0.0) - (
                red_player["logit_delta"] if red_player else 0.0
            )
            final_wr = lane_wr
            if player_adj != 0.0:
                final_wr = 1 / (1 + math.exp(-(logit(lane_wr) + player_adj)))

            lanes.append(
                {
                    "position": pos,
                    "blue": b, "blue_id": profile[b]["id"],
                    "red": r, "red_id": profile[r]["id"],
                    "matchup_games": games,
                    "blue_lane_win_rate": round(final_wr, 4),
                    "composition_win_rate": round(lane_wr, 4),
                    "source": source,
                    "blue_player": blue_player,
                    "red_player": red_player,
                }
            )

        def team_synergies(team: dict[str, str]) -> list[dict]:
            names = list(team.values())
            out = []
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = names[i], names[j]
                    cur.execute(
                        """SELECT COUNT(*), AVG(p1.win::int)
                           FROM participants p1
                           JOIN participants p2 ON p2.match_id = p1.match_id
                            AND p2.team_id = p1.team_id AND p2.champion_name = %s
                           WHERE p1.champion_name = %s""",
                        (b, a),
                    )
                    games, wr = cur.fetchone()
                    if games < 20 or wr is None:
                        continue
                    expected = (profile[a]["wr"] + profile[b]["wr"]) / 2
                    out.append(
                        {
                            "a": a, "a_id": profile[a]["id"],
                            "b": b, "b_id": profile[b]["id"],
                            "games": games,
                            "win_rate": round(float(wr), 4),
                            "delta": round(float(wr) - expected, 4),
                        }
                    )
            out.sort(key=lambda s: abs(s["delta"]), reverse=True)
            return out

        blue_syn = team_synergies(comp.blue) if len(comp.blue) >= 2 else []
        red_syn = team_synergies(comp.red) if len(comp.red) >= 2 else []

    # estimativa: média dos log-odds dos matchups de lane (já com o ajuste
    # de jogador aplicado) + ajuste leve de sinergia
    lane_score = sum(logit(l["blue_lane_win_rate"]) for l in lanes) / len(lanes)
    syn_adj = (
        (sum(s["delta"] for s in blue_syn) / len(blue_syn) if blue_syn else 0)
        - (sum(s["delta"] for s in red_syn) / len(red_syn) if red_syn else 0)
    )
    estimate = 1 / (1 + math.exp(-(lane_score + syn_adj)))

    # estado da partida (opcional): combina a composição com o modelo ML da
    # fase em log-odds — logit(combinado) = logit(ML) + logit(composição).
    # O termo ML já carrega a taxa-base (viés de lado) e o estado; a
    # composição entra como evidência extra centrada em 50%.
    state_analysis = None
    if comp.state is not None:
        if not _models:
            raise HTTPException(
                status_code=503,
                detail="Modelos não exportados — rode: python -m src.models.export_model",
            )
        if comp.state.minute not in _models:
            raise HTTPException(
                status_code=400,
                detail=f"minute deve ser um dos cortes disponíveis: {sorted(_models)}",
            )
        model = _models[comp.state.minute]
        X = pd.DataFrame([[getattr(comp.state, f) for f in FEATURES]], columns=FEATURES)
        ml_prob = float(model.predict_proba(X)[0, 1])
        X0 = pd.DataFrame([[0.0] * len(FEATURES)], columns=FEATURES)
        base_prob = float(model.predict_proba(X0)[0, 1])
        combined = 1 / (1 + math.exp(-(logit(ml_prob) + logit(estimate))))
        state_analysis = {
            "minute": comp.state.minute,
            "ml_probability": round(ml_prob, 4),
            "base_probability": round(base_prob, 4),
            "combined_probability": round(combined, 4),
            "note": (
                "Combinação em log-odds: o modelo ML avalia o estado da partida "
                "(incluindo a taxa-base com o viés de lado) e a composição entra "
                "como evidência adicional."
            ),
        }

    return {
        "lanes": lanes,
        "synergies": {"blue": blue_syn[:5], "red": red_syn[:5]},
        "estimate": {
            "blue_win_probability": round(estimate, 4),
            "lanes_used": len(lanes),
            "note": (
                "Estimativa heurística por matchups históricos de lane e sinergia de duplas "
                "— não é o modelo ML de estado de partida. Não inclui o viés de lado."
            ),
        },
        "state_analysis": state_analysis,
    }


# ---------------- competitivo (pro play, Oracle's Elixir) ----------------

def _pro_year(cur, year: int | None) -> int:
    """Ano efetivo das consultas pro (padrão: o mais recente carregado).
    O dataset tem 13 anos (2014-2026) — sem o filtro, as páginas
    misturariam metas de eras completamente diferentes."""
    if year is not None:
        return year
    cur.execute("SELECT MAX(year) FROM pro_games")
    latest = cur.fetchone()[0]
    if latest is None:
        raise HTTPException(
            status_code=503,
            detail="Sem dados competitivos — rode: python -m src.etl.load_pro (ver docs/scripts.md).",
        )
    return latest


@app.get("/stats/pro/years")
def pro_years():
    """Anos disponíveis no dataset competitivo (para o seletor da página)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT year, COUNT(DISTINCT game_id) FROM pro_games
               GROUP BY year ORDER BY year DESC"""
        )
        return [{"year": r[0], "games": r[1]} for r in cur.fetchall()]


@app.get("/stats/pro/overview")
def pro_overview(year: int | None = None):
    """Visão geral do dataset competitivo: jogos, ligas, viés de lado e
    duração — os números que ancoram a comparação solo queue × pro."""
    with get_conn() as conn, conn.cursor() as cur:
        year = _pro_year(cur, year)
        cur.execute(
            "SELECT COUNT(DISTINCT game_id) FROM pro_games WHERE year = %s", (year,)
        )
        games = cur.fetchone()[0]
        if games == 0:
            raise HTTPException(status_code=404, detail=f"Sem jogos no ano {year}.")
        cur.execute(
            "SELECT AVG(win::int) FROM pro_games WHERE side = 'Blue' AND year = %s", (year,)
        )
        blue_wr = cur.fetchone()[0]
        cur.execute(
            "SELECT AVG(game_length_s) / 60.0 FROM pro_games WHERE year = %s", (year,)
        )
        avg_min = cur.fetchone()[0]
        cur.execute(
            """SELECT league, COUNT(DISTINCT game_id) AS games,
                      AVG(CASE WHEN side = 'Blue' THEN win::int END) AS blue_wr
               FROM pro_games WHERE year = %s GROUP BY league
               ORDER BY games DESC LIMIT 12""",
            (year,),
        )
        leagues = [
            {"league": r[0], "games": r[1], "blue_win_rate": round(float(r[2]), 4)}
            for r in cur.fetchall()
        ]
    return {
        "year": year,
        "games": games,
        "blue_win_rate": round(float(blue_wr), 4),
        "avg_game_min": round(float(avg_min), 1),
        "leagues": leagues,
    }


@app.get("/stats/pro/gold15")
def pro_gold15(year: int | None = None):
    """Win rate do lado azul por faixa de diferença de ouro aos 15 min no
    COMPETITIVO — mesmas faixas do /stats/gold15 (solo queue) para
    comparação direta. Usa as linhas do lado azul (diff na perspectiva
    do azul, como nas features de solo queue)."""
    with get_conn() as conn, conn.cursor() as cur:
        year = _pro_year(cur, year)
        cur.execute(
            """SELECT width_bucket(LEAST(GREATEST(gold_diff_at15, -7999), 7999),
                                   -8000, 8000, 8) AS bucket,
                      AVG(win::int) AS wr, COUNT(*) AS n
               FROM pro_games
               WHERE side = 'Blue' AND gold_diff_at15 IS NOT NULL AND year = %s
               GROUP BY bucket ORDER BY bucket""",
            (year,),
        )
        rows = {r[0]: (float(r[1]), r[2]) for r in cur.fetchall()}
    out = []
    for b in range(1, 9):
        left = -8000 + (b - 1) * 2000
        mid = left + 1000
        wr, n = rows.get(b, (None, 0))
        out.append(
            {
                "gold_diff_mid": mid,
                "label": f"{left // 1000:+d}k a {(left + 2000) // 1000:+d}k",
                "blue_win_rate": round(wr, 4) if wr is not None else None,
                "matches": n,
            }
        )
    return out


@app.get("/stats/pro/champions")
def pro_champions(limit: int = 15, year: int | None = None):
    """Campeões mais presentes no competitivo, com o win rate deles no
    NOSSO solo queue ao lado (quando os nomes casam — o Oracle's Elixir
    usa nome de exibição, a Riot API usa nome interno; normalizamos
    removendo não-letras + mapeando os casos especiais)."""
    limit = max(1, min(limit, 50))
    with get_conn() as conn, conn.cursor() as cur:
        year = _pro_year(cur, year)
        cur.execute(
            """WITH year_games AS (
                   SELECT DISTINCT game_id FROM pro_games WHERE year = %s
               ),
               pro AS (
                   SELECT pp.champion, COUNT(*) AS games, AVG(pp.win::int) AS wr,
                          lower(regexp_replace(
                              CASE pp.champion
                                  WHEN 'Wukong' THEN 'MonkeyKing'
                                  WHEN 'Renata Glasc' THEN 'Renata'
                                  WHEN 'Nunu & Willump' THEN 'Nunu'
                                  ELSE pp.champion
                              END, '[^a-zA-Z]', '', 'g')) AS norm
                   FROM pro_players pp JOIN year_games yg ON yg.game_id = pp.game_id
                   GROUP BY pp.champion
               ),
               solo AS (
                   SELECT lower(champion_name) AS norm, MIN(champion_id) AS champion_id,
                          COUNT(*) AS games, AVG(win::int) AS wr
                   FROM participants GROUP BY lower(champion_name)
               ),
               total AS (SELECT COUNT(*)::float AS n FROM year_games)
               SELECT p.champion, p.games, p.wr,
                      p.games / t.n AS presence,
                      s.champion_id, s.games, s.wr
               FROM pro p CROSS JOIN total t
               LEFT JOIN solo s ON s.norm = p.norm
               ORDER BY p.games DESC LIMIT %s""",
            (year, limit),
        )
        rows = cur.fetchall()
    return [
        {
            "champion": r[0],
            "pro_games": r[1],
            "pro_win_rate": round(float(r[2]), 4),
            "presence": round(float(r[3]), 4),
            "champion_id": r[4],
            "solo_games": r[5],
            "solo_win_rate": round(float(r[6]), 4) if r[6] is not None else None,
        }
        for r in rows
    ]


# ---------------- linguagem natural ----------------

@app.post("/ask")
def ask_nl(q: Question):
    try:
        result = ask(q.question, [t.model_dump() for t in q.history])
    except ValueError as exc:
        # bloqueado pela validação de segurança (query não-SELECT, tabela
        # não permitida, múltiplos statements etc.) — não é falha nossa
        raise HTTPException(status_code=400, detail=str(exc))
    except SqlExecutionError as exc:
        # a SQL passou na validação mas o banco rejeitou (coluna/tabela
        # inexistente, erro de sintaxe) — mostra a SQL e o erro real do
        # banco para dar pra debugar o prompt/schema, não só "tente de novo"
        raise HTTPException(
            status_code=422,
            detail={
                "message": "A consulta gerada falhou ao executar no banco.",
                "sql": exc.sql,
                "cause": str(exc.cause).strip(),
            },
        )
    except Exception as exc:
        raise _external_call_error(exc)
    return {
        "sql": result["sql"],
        "columns": result["columns"],
        "rows": [list(r) for r in result["rows"][:100]],
    }


@app.post("/ask/explain")
def ask_explain(req: ExplainRequest):
    try:
        explanation = explain_result(
            req.question, req.sql, req.columns, [tuple(r) for r in req.rows]
        )
    except Exception as exc:
        raise _external_call_error(exc)
    return {"explanation": explanation}


# ---------------- predição ----------------

@app.post("/predict")
def predict(state: MatchState):
    if not _models:
        raise HTTPException(
            status_code=503,
            detail="Modelos não exportados — rode: python -m src.models.export_model",
        )
    if state.minute not in _models:
        raise HTTPException(
            status_code=400,
            detail=f"minute deve ser um dos cortes disponíveis: {sorted(_models)}",
        )
    try:
        model = _models[state.minute]
        X = pd.DataFrame([[getattr(state, f) for f in FEATURES]], columns=FEATURES)
        prob = float(model.predict_proba(X)[0, 1])
        shap_values = _explainers[state.minute](X)
        contributions = {
            feat: float(shap_values.values[0, i]) for i, feat in enumerate(FEATURES)
        }
    except Exception as exc:
        raise _external_call_error(exc)
    return {
        "blue_win_probability": prob,
        "shap_contributions": contributions,
        "minute": state.minute,
    }
