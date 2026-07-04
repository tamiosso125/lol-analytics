"""Passo 1 — Semear a tabela de jogadores com os ladders Challenger/Grandmaster.

Uso:  python -m src.collect.seed_players
"""
import psycopg2.extras

from src.db import get_conn
from src.riot.client import RiotClient
from src.config import RIOT_PLATFORM

UPSERT = """
INSERT INTO players (puuid, tier, division, league_points, platform)
VALUES %s
ON CONFLICT (puuid) DO UPDATE
SET tier = EXCLUDED.tier,
    league_points = EXCLUDED.league_points,
    updated_at = now();
"""


def main() -> None:
    client = RiotClient()
    rows = []
    for tier_name, fetch in [
        ("CHALLENGER", client.challenger_league),
        ("GRANDMASTER", client.grandmaster_league),
    ]:
        league = fetch()
        for e in league.get("entries", []):
            puuid = e.get("puuid")
            if not puuid:
                # ligas antigas retornavam apenas summonerId; entradas sem
                # puuid são ignoradas nesta versão inicial
                continue
            rows.append((puuid, tier_name, e.get("rank"), e.get("leaguePoints"), RIOT_PLATFORM))

    with get_conn() as conn, conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, UPSERT, rows)
    print(f"{len(rows)} jogadores inseridos/atualizados.")


if __name__ == "__main__":
    main()
