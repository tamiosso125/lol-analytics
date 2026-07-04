"""Conexão simples com o PostgreSQL."""
import psycopg2
import psycopg2.extras

from src.config import DATABASE_URL


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_schema(schema_path: str = "db/schema.sql") -> None:
    with open(schema_path, encoding="utf-8") as f:
        sql = f.read()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
    print("Schema aplicado.")


if __name__ == "__main__":
    init_schema()
