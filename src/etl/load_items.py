"""ETL — extrai compras/vendas de itens das timelines para item_events.

Os eventos ITEM_* do match-v5 registram cada clique na loja, incluindo
os desfeitos. Este ETL aplica os ITEM_UNDO antes de gravar: um UNDO com
beforeId=X remove a compra mais recente de X (e com afterId=Y, a venda
mais recente de Y) — a tabela final reflete o que o jogador de fato
manteve. ITEM_DESTROYED (componente consumido numa receita, consumível
usado) não é gravado: para análise de build interessa o que foi
comprado, não a fusão de componentes.

A tabela é reconstruída do zero a cada execução (TRUNCATE) — só este
script escreve nela, e reprocessar tudo leva ~1-2 min.

Uso:  python -m src.etl.load_items
"""
from psycopg2.extras import execute_values

from src.db import get_conn


def item_rows_from_timeline(match_id: str, payload: dict) -> list[tuple]:
    """Linhas (match_id, puuid, ts_ms, item_id, action) com UNDO aplicado."""
    info = payload.get("info", {})
    puuid_by_pid = {
        p.get("participantId"): p.get("puuid") for p in info.get("participants", [])
    }

    # eventos por participante, em ordem, para poder desfazer o mais recente
    per_pid: dict[int, list[list]] = {}
    for frame in info.get("frames", []):
        for ev in frame.get("events", []):
            t = ev.get("type")
            pid = ev.get("participantId")
            if pid not in puuid_by_pid:
                continue  # participantId 0 = eventos de sistema (ex.: item inicial de suporte)
            events = per_pid.setdefault(pid, [])
            if t == "ITEM_PURCHASED":
                events.append(["BUY", ev.get("timestamp", 0), ev.get("itemId")])
            elif t == "ITEM_SOLD":
                events.append(["SELL", ev.get("timestamp", 0), ev.get("itemId")])
            elif t == "ITEM_UNDO":
                # desfaz a ação mais recente com aquele item (compra se
                # beforeId, venda se afterId) — varre de trás pra frente
                target_action, target_item = (
                    ("BUY", ev.get("beforeId")) if ev.get("beforeId") else ("SELL", ev.get("afterId"))
                )
                for i in range(len(events) - 1, -1, -1):
                    if events[i][0] == target_action and events[i][2] == target_item:
                        del events[i]
                        break

    return [
        (match_id, puuid_by_pid[pid], ts, item_id, action)
        for pid, events in per_pid.items()
        for action, ts, item_id in events
    ]


def reprocess_all() -> None:
    # duas conexões: cursor nomeado (server-side) exige transação, então a
    # leitura fica numa conexão transacional e a escrita numa autocommit
    read_conn = get_conn()
    write_conn = get_conn()
    write_conn.autocommit = True

    with write_conn.cursor() as cur:
        cur.execute("TRUNCATE item_events")

    n_matches, n_rows, batch = 0, 0, []
    with read_conn.cursor("tl_items") as cur:
        cur.itersize = 100
        # join com matches: raw_timelines tem remakes (<5 min) que o ETL
        # principal pula — sem o filtro, o insert viola a FK de match_id
        cur.execute(
            """SELECT t.match_id, t.payload
               FROM raw_timelines t JOIN matches m USING (match_id)"""
        )
        for match_id, payload in cur:
            batch.extend(item_rows_from_timeline(match_id, payload))
            n_matches += 1
            if len(batch) >= 5000:
                with write_conn.cursor() as wcur:
                    execute_values(
                        wcur,
                        "INSERT INTO item_events (match_id, puuid, ts_ms, item_id, action) VALUES %s",
                        batch,
                    )
                n_rows += len(batch)
                batch = []
            if n_matches % 1000 == 0:
                print(f"{n_matches} timelines processadas ({n_rows} eventos)")
    if batch:
        with write_conn.cursor() as wcur:
            execute_values(
                wcur,
                "INSERT INTO item_events (match_id, puuid, ts_ms, item_id, action) VALUES %s",
                batch,
            )
        n_rows += len(batch)

    read_conn.close()
    write_conn.close()
    print(f"Concluído: {n_matches} timelines -> {n_rows} eventos em item_events.")


if __name__ == "__main__":
    reprocess_all()
