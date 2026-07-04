"""ETL — normaliza o JSON do match-v5 nas tabelas matches/teams/participants.

Pode ser chamado partida a partida (load_one, usado pelo coletor) ou
reprocessar tudo que está em raw_matches:

Uso:  python -m src.etl.load_matches
"""
from datetime import datetime, timezone

from src.db import get_conn


def load_one(conn, match: dict) -> None:
    info = match["info"]
    meta = match["metadata"]
    mid = meta["matchId"]

    # ignora remakes (< 5 min) e filas não ranqueadas
    if info.get("gameDuration", 0) < 300:
        return

    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO matches
               (match_id, platform_id, queue_id, game_version, game_creation, game_duration_s)
               VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (
                mid,
                info.get("platformId"),
                info.get("queueId"),
                info.get("gameVersion"),
                datetime.fromtimestamp(info["gameCreation"] / 1000, tz=timezone.utc),
                info.get("gameDuration"),
            ),
        )
        for t in info.get("teams", []):
            obj = t.get("objectives", {})
            cur.execute(
                """INSERT INTO teams
                   (match_id, team_id, win, barons, dragons, heralds, towers, inhibitors)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (
                    mid,
                    t["teamId"],
                    t.get("win"),
                    obj.get("baron", {}).get("kills"),
                    obj.get("dragon", {}).get("kills"),
                    obj.get("riftHerald", {}).get("kills"),
                    obj.get("tower", {}).get("kills"),
                    obj.get("inhibitor", {}).get("kills"),
                ),
            )
            for b in t.get("bans", []):
                if b.get("championId", -1) < 0:
                    continue  # -1 = jogador não baniu ninguém
                cur.execute(
                    """INSERT INTO bans (match_id, team_id, pick_turn, champion_id)
                       VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                    (mid, t["teamId"], b.get("pickTurn"), b.get("championId")),
                )
        for p in info.get("participants", []):
            cur.execute(
                """INSERT INTO participants
                   (match_id, puuid, team_id, team_position, champion_id, champion_name,
                    kills, deaths, assists, gold_earned, cs_total, vision_score,
                    dmg_to_champions, win)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT DO NOTHING""",
                (
                    mid,
                    p["puuid"],
                    p.get("teamId"),
                    p.get("teamPosition"),
                    p.get("championId"),
                    p.get("championName"),
                    p.get("kills"),
                    p.get("deaths"),
                    p.get("assists"),
                    p.get("goldEarned"),
                    (p.get("totalMinionsKilled", 0) + p.get("neutralMinionsKilled", 0)),
                    p.get("visionScore"),
                    p.get("totalDamageDealtToChampions"),
                    p.get("win"),
                ),
            )


def reprocess_all() -> None:
    # duas conexões: cursor nomeado (server-side) exige transação, então a
    # leitura fica numa conexão transacional e a escrita numa autocommit
    read_conn = get_conn()
    write_conn = get_conn()
    write_conn.autocommit = True
    with read_conn.cursor("raw") as cur:
        cur.itersize = 200
        cur.execute("SELECT payload FROM raw_matches")
        n = 0
        for (payload,) in cur:
            load_one(write_conn, payload)
            n += 1
            if n % 500 == 0:
                print(f"{n} partidas processadas")
    read_conn.close()
    write_conn.close()
    print(f"Reprocessamento concluído: {n} partidas.")


if __name__ == "__main__":
    reprocess_all()
