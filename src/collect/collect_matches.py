"""Passo 2 — Coletar partidas ranqueadas dos jogadores semeados.

Para cada jogador: lista os últimos match_ids (fila 420) e baixa
match + timeline dos que ainda não estão no banco. JSON bruto vai
para raw_matches/raw_timelines; a normalização é feita pelo ETL.

Multi-região (planejamento v2, sprint 5): os jogadores são agrupados
por platform (coluna já existe em players, preenchida por
seed_players); cada grupo usa um RiotClient roteado pra região certa
(americas/asia/europe/sea — ver src/riot/client.py). Sequencial entre
plataformas, não paralelo — mesmo quando duas plataformas roteiam para
a mesma região (ex.: br1 e na1 -> americas), evita estourar o limite
real da Riot por região.

Uso:  python -m src.collect.collect_matches --players 50 --matches-per-player 20
      python -m src.collect.collect_matches --platforms kr euw1 --players 20 --matches-per-player 10
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


def collect_for_platform(
    conn, client: RiotClient, puuids: list[str], per_player: int, with_timeline: bool, seen: set[str]
) -> int:
    new = 0
    for i, puuid in enumerate(puuids, 1):
        try:
            ids = client.match_ids_by_puuid(puuid, count=per_player)
        except Exception as exc:  # jogador pode ter restrições
            print(f"  [{i}/{len(puuids)}] erro em match_ids: {exc}")
            continue
        for mid in ids:
            if mid in seen:
                continue
            try:
                match = client.match(mid)
                timeline = client.timeline(mid) if with_timeline else None
            except Exception as exc:
                print(f"    erro em {mid}: {exc}")
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
        print(f"  [{i}/{len(puuids)}] total novo (nesta plataforma): {new}")
    return new


def main(platforms: list[str] | None, n_players: int, per_player: int, with_timeline: bool) -> None:
    conn = get_conn()
    conn.autocommit = True
    seen = known_match_ids(conn)
    print(f"{len(seen)} partidas já no banco.")

    with conn.cursor() as cur:
        if platforms:
            cur.execute(
                """SELECT platform, puuid FROM players WHERE platform = ANY(%s)
                   ORDER BY platform, league_points DESC""",
                (platforms,),
            )
        else:
            cur.execute("SELECT platform, puuid FROM players ORDER BY platform, league_points DESC")
        by_platform: dict[str, list[str]] = {}
        for platform, puuid in cur.fetchall():
            by_platform.setdefault(platform, []).append(puuid)

    total_new = 0
    for platform, all_puuids in by_platform.items():
        puuids = all_puuids[:n_players]
        print(f"\n=== {platform}: {len(puuids)} jogador(es) ===")
        client = RiotClient(platform=platform)
        total_new += collect_for_platform(conn, client, puuids, per_player, with_timeline, seen)

    conn.close()
    print(f"\nColeta encerrada: {total_new} partidas novas em {len(by_platform)} plataforma(s).")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--platforms", nargs="+", default=None, help="filtra plataformas (padrão: todas em players)")
    p.add_argument("--players", type=int, default=50, help="jogadores por plataforma")
    p.add_argument("--matches-per-player", type=int, default=20)
    p.add_argument("--no-timeline", action="store_true")
    args = p.parse_args()
    main(args.platforms, args.players, args.matches_per_player, not args.no_timeline)
