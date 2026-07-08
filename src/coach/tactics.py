"""Contexto tático derivado da timeline de uma partida real.

Ponte entre a Camada 2 (itens — dado que a Riot grava) e o INÍCIO da
Camada 3 (sinais espaciais/táticos derivados das posições — dado que a
Riot grava por minuto, mas que ninguém entrega "mastigado": agrupamento,
overextensão, tempo de selva). Ver docs/diario_execucao.md 2026-07-08.

LIMITE HONESTO: isto usa posição a 1 amostra/minuto (participantFrames)
— dá pra dizer "os 5 estão agrupados no meio" ou "o atirador está
avançado na metade inimiga", mas NÃO o estado de wave/minion (não existe
em nenhuma versão da match-v5; só via parsing de replay .rofl ou visão
computacional — esse é o resto da Camada 3, ainda bloqueado). O
consumidor (advice.py) rotula tudo como aproximado.
"""
import math

from src.db import get_conn


def _team(participant_id: int) -> int:
    """participantId 1-5 = azul (100), 6-10 = vermelho (200)."""
    return 100 if participant_id <= 5 else 200


def tactical_context(
    match_id: str,
    minute: int,
    items_catalog: dict,
    completed_ids: set[int],
) -> dict | None:
    """Retorna itens finalizados possuídos por campeão + sinais espaciais
    no `minute` dado; None se a partida não tem timeline."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT payload FROM raw_timelines WHERE match_id = %s", (match_id,))
        row = cur.fetchone()
        if row is None:
            return None
        payload = row[0]
        cur.execute(
            "SELECT puuid, champion_name FROM participants WHERE match_id = %s", (match_id,)
        )
        champ_by_puuid = dict(cur.fetchall())

        # itens finalizados possuídos por puuid ATÉ o minuto (compra menos
        # venda; item_events já tem ITEM_UNDO aplicado no ETL)
        cutoff_ms = minute * 60_000
        cur.execute(
            """SELECT puuid, item_id,
                      SUM(CASE WHEN action='BUY' THEN 1 ELSE -1 END) AS net
               FROM item_events
               WHERE match_id = %s AND ts_ms <= %s AND item_id = ANY(%s)
               GROUP BY puuid, item_id HAVING SUM(CASE WHEN action='BUY' THEN 1 ELSE -1 END) > 0""",
            (match_id, cutoff_ms, list(completed_ids)),
        )
        items_by_puuid: dict[str, list[str]] = {}
        for puuid, item_id, _net in cur.fetchall():
            name = items_catalog.get(str(item_id), {}).get("name", f"Item {item_id}")
            items_by_puuid.setdefault(puuid, []).append(name)

    info = payload.get("info", {})
    # participantId -> puuid (via lista de participantes da timeline)
    puuid_by_pid = {
        p["participantId"]: p.get("puuid") for p in info.get("participants", [])
    }

    items = {
        champ_by_puuid.get(puuid_by_pid.get(pid), f"P{pid}"): items_by_puuid.get(
            puuid_by_pid.get(pid, ""), []
        )
        for pid in range(1, 11)
        if items_by_puuid.get(puuid_by_pid.get(pid, ""))
    }

    frames = info.get("frames", [])
    if minute >= len(frames):
        return {"minute": minute, "items": items}
    pframes = frames[minute].get("participantFrames", {})

    # bounds oficiais do mapa 11 (mesmos do /matches/{id}/positions)
    MIN, MAX = -120, 14980
    norm = lambda v: (v - MIN) / (MAX - MIN)

    pos = {100: [], 200: []}
    jungle = {100: 0, 200: 0}
    for pf in pframes.values():
        pid = pf.get("participantId")
        p = pf.get("position")
        if not pid or p is None:
            continue
        t = _team(pid)
        pos[t].append((norm(p["x"]), norm(p["y"])))
        jungle[t] += pf.get("jungleMinionsKilled", 0)

    spatial = {}
    for team, label in ((100, "blue"), (200, "red")):
        pts = pos[team]
        if len(pts) < 2:
            continue
        cx = sum(x for x, _ in pts) / len(pts)
        cy = sum(y for _, y in pts) / len(pts)
        spread = sum(math.hypot(x - cx, y - cy) for x, y in pts) / len(pts)
        # rio = anti-diagonal nx+ny=1; azul avança quando nx+ny>1, vermelho <1
        if team == 100:
            overext = sum(1 for x, y in pts if x + y > 1.05)
            deep = sum(1 for x, y in pts if x + y > 1.30)
        else:
            overext = sum(1 for x, y in pts if x + y < 0.95)
            deep = sum(1 for x, y in pts if x + y < 0.70)
        spatial[label] = {
            # spread normalizado: < 0.14 agrupado, > 0.30 espalhado
            "grouping": "agrupados" if spread < 0.14 else "espalhados" if spread > 0.30 else "parcialmente agrupados",
            "overextended": overext,
            "deep_overextended": deep,
        }

    return {
        "minute": minute,
        "items": items,
        "spatial": spatial,
        # tempo de selva (jungleMinionsKilled) azul menos vermelho
        "jungle_diff": jungle[100] - jungle[200],
    }
