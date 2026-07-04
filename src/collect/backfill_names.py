"""Backfill de gameName/tagLine dos jogadores via account-v1.

O endpoint de liga (seed_players) não retorna mais nomes — só puuid.
Este script busca o nome dos jogadores com mais partidas coletadas
(1 requisição por jogador, respeitando o rate limit do cliente).

Uso:  python -m src.collect.backfill_names --min-games 20
"""
import argparse

from src.db import get_conn
from src.riot.client import RiotClient


def main(min_games: int) -> None:
    client = RiotClient()
    conn = get_conn()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(
            """SELECT p.puuid FROM players p
               JOIN participants pt ON pt.puuid = p.puuid
               WHERE p.game_name IS NULL
               GROUP BY p.puuid HAVING COUNT(*) >= %s""",
            (min_games,),
        )
        puuids = [r[0] for r in cur.fetchall()]
    print(f"{len(puuids)} jogadores sem nome (>= {min_games} jogos).")

    ok = 0
    for i, puuid in enumerate(puuids, 1):
        try:
            acc = client.account_by_puuid(puuid)
        except Exception as exc:
            print(f"[{i}/{len(puuids)}] erro: {exc}")
            continue
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE players SET game_name = %s, tag_line = %s WHERE puuid = %s",
                (acc.get("gameName"), acc.get("tagLine"), puuid),
            )
        ok += 1
        if i % 20 == 0:
            print(f"[{i}/{len(puuids)}] {ok} nomes preenchidos")
    conn.close()
    print(f"Backfill concluído: {ok}/{len(puuids)} nomes.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--min-games", type=int, default=20)
    args = p.parse_args()
    main(args.min_games)
