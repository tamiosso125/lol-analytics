"""Passo 1 — Semear a tabela de jogadores com os ladders Challenger/
Grandmaster/Master.

Multi-região (planejamento v2, sprint 5): aceita várias plataformas
numa só chamada — cada uma vira uma instância de RiotClient própria
(rate limit por instância, ver src/riot/client.py). platform é gravado
por linha, então players/matches/participants já convivem com vários
recortes no mesmo banco.

Uso:  python -m src.collect.seed_players
      python -m src.collect.seed_players --platforms br1 kr euw1 na1
      python -m src.collect.seed_players --platforms kr --tiers CHALLENGER MASTER
"""
import argparse

import psycopg2.extras

from src.db import get_conn
from src.riot.client import RiotClient

UPSERT = """
INSERT INTO players (puuid, tier, division, league_points, platform)
VALUES %s
ON CONFLICT (puuid) DO UPDATE
SET tier = EXCLUDED.tier,
    league_points = EXCLUDED.league_points,
    platform = EXCLUDED.platform,
    updated_at = now();
"""

TIER_FETCHERS = {
    "CHALLENGER": lambda c: c.challenger_league(),
    "GRANDMASTER": lambda c: c.grandmaster_league(),
    "MASTER": lambda c: c.master_league(),
}


def main(platforms: list[str], tiers: list[str]) -> None:
    total = 0
    for platform in platforms:
        client = RiotClient(platform=platform)
        rows = []
        for tier_name in tiers:
            league = TIER_FETCHERS[tier_name](client)
            for e in league.get("entries", []):
                puuid = e.get("puuid")
                if not puuid:
                    # ligas antigas retornavam apenas summonerId; entradas
                    # sem puuid são ignoradas nesta versão inicial
                    continue
                rows.append((puuid, tier_name, e.get("rank"), e.get("leaguePoints"), platform))

        with get_conn() as conn, conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, UPSERT, rows)
        print(f"{platform}: {len(rows)} jogadores inseridos/atualizados.")
        total += len(rows)
    print(f"Total: {total} jogadores em {len(platforms)} plataforma(s).")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--platforms", nargs="+", default=None, help="ex.: br1 kr euw1 na1 (padrão: RIOT_PLATFORM do .env)")
    p.add_argument(
        "--tiers", nargs="+", default=["CHALLENGER", "GRANDMASTER"],
        choices=list(TIER_FETCHERS), help="CHALLENGER GRANDMASTER MASTER",
    )
    args = p.parse_args()
    from src.config import RIOT_PLATFORM

    main(args.platforms or [RIOT_PLATFORM], args.tiers)
