"""ETL — carrega data/items.json (catálogo Data Dragon) na tabela `items`.

Diferente de load_items.py (que extrai COMPRAS de item por partida, de
item_events): este script carrega o CATÁLOGO — nome, custo, se é válido
no mapa 11 — pra permitir JOIN em SQL (NLQ) e pegar nome de item a
partir do item_id numérico de item_events. Sem isso, uma pergunta como
"quais os itens mais construídos pela Camille?" no /consulta não tem
como responder com nome de item — só teria o número, e pedir pra LLM
"lembrar" nome de item por ID de cabeça já causou um bug real no coach
(ver docs/diario_execucao.md 2026-07-08).

A tabela é reconstruída do zero a cada execução (TRUNCATE) — só este
script escreve nela; rodar de novo se `data/items.json` mudar de versão.

Uso:  python -m src.etl.load_item_catalog
"""
import json

from psycopg2.extras import execute_values

from src.db import get_conn

ITEMS_PATH = "data/items.json"


def main() -> None:
    with open(ITEMS_PATH, encoding="utf-8") as f:
        catalog = json.load(f)

    rows = [
        (
            int(item_id),
            it.get("name"),
            it.get("total_gold", 0),
            bool(it.get("purchasable")),
            bool(it.get("maps", {}).get("11")),
        )
        for item_id, it in catalog.items()
    ]

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE items")
        execute_values(
            cur,
            "INSERT INTO items (item_id, name, total_gold, purchasable, map_11) VALUES %s",
            rows,
        )
        conn.commit()

    print(f"Concluído: {len(rows)} itens carregados em `items`.")


if __name__ == "__main__":
    main()
