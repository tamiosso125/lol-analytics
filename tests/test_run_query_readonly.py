"""Testa que `run_query` roda em transação SOMENTE LEITURA (precisa do banco, sem API).

Mesmo que o validador falhasse, o banco recusa escrita. Usa uma tabela temporária
(some ao fechar a conexão) para não tocar nos dados.

Uso:  .venv\\Scripts\\python.exe tests\\test_run_query_readonly.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2

from src.nlq.nl_to_sql import run_query

print("run_query em transacao somente leitura")

cols, rows = run_query("SELECT current_setting('transaction_read_only')")
assert rows == [("on",)], rows

cols, rows = run_query("SELECT COUNT(*) FROM matches")
assert rows[0][0] > 0

for sql in ("CREATE TEMP TABLE _t_ro(x int)", "UPDATE matches SET queue_id = queue_id WHERE false"):
    try:
        run_query(sql)
    except psycopg2.Error as exc:
        msg = str(exc).lower()
        assert any(k in msg for k in ("leitura-apenas", "somente leitura", "read-only")), exc
    else:
        raise AssertionError(f"escrita passou: {sql}")

print("OK")
