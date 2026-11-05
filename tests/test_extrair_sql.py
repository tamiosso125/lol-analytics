"""Testa `extrair_sql` (src/nlq/nl_to_sql.py), sem banco nem API.

Quando o modelo escreve uma SQL, comenta e escreve outra, vale a última; o texto puro
e o bloco único continuam como sempre. Caso real: pergunta 86 do conjunto cego, que
voltava "Múltiplos statements" em todas as passadas.

Uso:  python tests/test_extrair_sql.py (com a .venv)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.nlq.nl_to_sql import extrair_sql
from src.nlq.sql_guard import validate_sql

print("extração da SQL")

# 1. SQL pura
assert extrair_sql("SELECT 1;") == "SELECT 1;"
# 2. bloco único com ```sql
assert extrair_sql("```sql\nSELECT 2;\n```") == "SELECT 2;"
# 3. bloco único sem a palavra sql
assert extrair_sql("```\nSELECT 3\n```") == "SELECT 3"
# 4. o caso real: SQL, fecha o bloco, "Wait", segunda SQL com bloco sem fechar
real = ("SELECT COUNT(DISTINCT g) FROM t GROUP BY g HAVING SUM(k) > 40;\n```\n\n"
        "Wait, let me reconsider. Fix:\n\n```sql\nSELECT COUNT(*) FROM (SELECT g FROM t "
        "GROUP BY g HAVING SUM(k) > 40) s;")
final = extrair_sql(real)
assert final.startswith("SELECT COUNT(*) FROM (SELECT g"), final
assert "Wait" not in final and "```" not in final
# 5. a SQL extraída passa pelo validador como qualquer outra (falha fechada)
validate_sql("SELECT COUNT(*) FROM (SELECT game_id FROM pro_games GROUP BY game_id) s")
# bloco que não começa com SELECT/WITH é ignorado: só o SELECT seguro seria executado
assert extrair_sql("```sql\nSELECT 1;\n```\n```sql\nDROP TABLE matches;\n```") == "SELECT 1;"
# escrita encadeada no MESMO bloco continua barrada pelo validador
try:
    validate_sql(extrair_sql("```sql\nSELECT 1; DROP TABLE matches;\n```"))
except ValueError:
    pass
else:
    raise AssertionError("a SQL perigosa passou")
# 6. com bloco de aviso (SELECT 'não é possível ...') também funciona
assert extrair_sql("```sql\nSELECT 'não é possível responder: x' AS aviso;\n```").startswith("SELECT 'não")
print("OK")
