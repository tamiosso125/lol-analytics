"""Passo 2 — Coletar partidas ranqueadas dos jogadores semeados.

Para cada jogador: lista os últimos match_ids (fila 420) e baixa
match + timeline dos que ainda não estão no banco. JSON bruto vai
para raw_matches/raw_timelines; a normalização é feita pelo ETL.

Uso:  python -m src.collect.collect_matches --players 50 --matches-per-player 20
"""
import argparse
import json

from src.db import get_conn
from src.etl.load_matches import load_one
from src.riot.client import RiotClient


def known_match_ids(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT match_id FROM raw_matches")
        return {r[0] for r in cur.fetchall()}


def main(n_players: int, per_player: int, with_timeline: bool) -> None:
    client = RiotClient()
    conn = get_conn()
    conn.autocommit = True
    seen = known_match_ids(conn)
    print(f"{len(seen)} partidas já no banco.")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT puuid FROM players ORDER BY league_points DESC LIMIT %s",
            (n_players,),
        )
        puuids = [r[0] for r in cur.fetchall()]

    new = 0
    for i, puuid in enumerate(puuids, 1):
        try:
            ids = client.match_ids_by_puuid(puuid, count=per_player)
        except Exception as exc:  # jogador pode ter restrições
            print(f"[{i}/{len(puuids)}] erro em match_ids: {exc}")
            continue
        for mid in ids:
            if mid in seen:
                continue
            try:
                match = client.match(mid)
                timeline = client.timeline(mid) if with_timeline else None
            except Exception as exc:
                print(f"  erro em {mid}: {exc}")
                continue
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO raw_matches (match_id, payload) VALUES (%s, %s) "
                    "ON CONFLICT DO NOTHING",
                    (mid, json.dumps(match)),
                )
                if timeline:
                    cur.execute(
                        "INSERT INTO raw_timelines (match_id, payload) VALUES (%s, %s) "
                        "ON CONFLICT DO NOTHING",
                        (mid, json.dumps(timeline)),
                    )
            load_one(conn, match)  # normaliza na hora
            seen.add(mid)
            new += 1
        print(f"[{i}/{len(puuids)}] total novo: {new}")

    conn.close()
    print(f"Coleta encerrada: {new} partidas novas.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--players", type=int, default=50)
    p.add_argument("--matches-per-player", type=int, default=20)
    p.add_argument("--no-timeline", action="store_true")
    args = p.parse_args()
    main(args.players, args.matches_per_player, not args.no_timeline)
