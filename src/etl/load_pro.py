"""ETL — carrega os CSVs do Oracle's Elixir em pro_games/pro_players.

O CSV tem 12 linhas por jogo: 10 de jogador (position top/jng/mid/bot/
sup) e 2 de time (position = 'team'). Linhas com datacompleteness
'partial' são carregadas mesmo assim (algumas ligas não reportam os
cortes de 15 min — as colunas ficam NULL), mas jogos sem game_id são
descartados. Idempotente por ano: apaga as linhas do(s) ano(s) sendo
recarregado(s) antes de inserir.

Uso:  python -m src.etl.load_pro            (todos os CSVs em data/pro/)
      python -m src.etl.load_pro --year 2026
"""
import argparse
import glob
import math
import os

import pandas as pd
from psycopg2.extras import execute_values

from src.db import get_conn


def _clean(v):
    """NaN do pandas -> None do SQL; floats inteiros -> int."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def load_csv(path: str) -> None:
    year = int(os.path.basename(path)[:4])
    df = pd.read_csv(path, low_memory=False)
    df = df[df["gameid"].notna()]
    print(f"{os.path.basename(path)}: {len(df)} linhas, {df['gameid'].nunique()} jogos")

    teams = df[df["position"] == "team"]
    players = df[df["position"] != "team"]

    game_rows = [
        tuple(
            _clean(v)
            for v in (
                r.gameid, r.league, r.year, r.split,
                bool(r.playoffs) if not pd.isna(r.playoffs) else None,
                r.date, str(r.patch) if not pd.isna(r.patch) else None,
                r.side, r.teamname,
                bool(r.result) if not pd.isna(r.result) else None,
                r.gamelength, r.kills, r.deaths,
                r.dragons, r.barons, r.heralds, r.towers, r.inhibitors,
                r.golddiffat15, r.xpdiffat15, r.csdiffat15,
            )
        )
        for r in teams.itertuples()
    ]
    player_rows = [
        tuple(
            _clean(v)
            for v in (
                r.gameid, r.side, r.position, r.playername, r.teamname,
                r.champion, r.kills, r.deaths, r.assists,
                bool(r.result) if not pd.isna(r.result) else None,
            )
        )
        for r in players.itertuples()
    ]

    conn = get_conn()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DELETE FROM pro_players WHERE game_id IN (SELECT game_id FROM pro_games WHERE year = %s)", (year,))
        cur.execute("DELETE FROM pro_games WHERE year = %s", (year,))
        execute_values(
            cur,
            """INSERT INTO pro_games
               (game_id, league, year, split, playoffs, game_date, patch, side,
                team_name, win, game_length_s, kills, deaths, dragons, barons,
                heralds, towers, inhibitors, gold_diff_at15, xp_diff_at15, cs_diff_at15)
               VALUES %s ON CONFLICT DO NOTHING""",
            game_rows,
            page_size=2000,
        )
        execute_values(
            cur,
            """INSERT INTO pro_players
               (game_id, side, position, player_name, team_name, champion,
                kills, deaths, assists, win)
               VALUES %s ON CONFLICT DO NOTHING""",
            player_rows,
            page_size=2000,
        )
    conn.close()
    print(f"  -> {len(game_rows)} linhas de time, {len(player_rows)} de jogador carregadas.")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=None)
    args = p.parse_args()

    pattern = (
        f"data/pro/{args.year}_LoL_esports_match_data_from_OraclesElixir.csv"
        if args.year
        else "data/pro/*_LoL_esports_match_data_from_OraclesElixir.csv"
    )
    files = sorted(glob.glob(pattern))
    if not files:
        print(
            f"Nenhum CSV em {pattern} — rode antes: python -m src.collect.collect_pro"
            + (f" --year {args.year}" if args.year else "")
        )
        return
    for f in files:
        load_csv(f)


if __name__ == "__main__":
    main()
