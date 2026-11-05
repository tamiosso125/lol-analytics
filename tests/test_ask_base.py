"""Testa a guarda de base e `ask_base` com falhas SIMULADAS (sem banco nem API).

Parte 1 — `tables_used` e `validate_base` (src/nlq/sql_guard.py): uma consulta não
pode misturar as tabelas do solo queue com as do competitivo.

Parte 2 — `ask_base` (src/nlq/nl_to_sql.py), com `generate_sql` e `run_query`
falsos:
  * a base chega ao gerador;
  * SQL que mistura as bases NÃO chega ao banco, e a nova tentativa recebe a
    mensagem de que usou a outra base;
  * se a correção ainda mistura, levanta BaseMixError e o banco nunca é tocado;
  * erro de banco continua sendo refeito uma vez, mantendo a base;
  * o aviso "não é possível responder" (sem tabela) passa em qualquer base.

Uso:  .venv\\Scripts\\python.exe tests\\test_ask_base.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import psycopg2.errors  # noqa: E402

from src.nlq import nl_to_sql  # noqa: E402
from src.nlq.sql_guard import BaseMixError, tables_used, validate_base  # noqa: E402

SOLO_OK = "SELECT COUNT(*) FROM matches m JOIN teams t ON t.match_id = m.match_id"
PRO_OK = "SELECT COUNT(DISTINCT game_id) FROM pro_games WHERE year = 2026"
MISTURA = "SELECT COUNT(*) FROM teams t JOIN pro_games pg ON pg.game_id = t.match_id"
AVISO = "SELECT 'não é possível responder: falta a coluna' AS aviso"


def parte1(falhas):
    def confere(cond, msg):
        if not cond:
            falhas.append(msg)

    confere(tables_used(SOLO_OK) == {"matches", "teams"}, f"tables_used solo: {tables_used(SOLO_OK)}")
    confere(tables_used(PRO_OK) == {"pro_games"}, f"tables_used pro: {tables_used(PRO_OK)}")
    confere(tables_used(AVISO) == set(), "aviso não tem tabela")
    confere(
        tables_used("WITH c AS (SELECT match_id FROM matches) SELECT COUNT(*) FROM c JOIN teams USING (match_id)")
        == {"matches", "teams"},
        "a CTE não conta como tabela",
    )
    confere(
        tables_used("SELECT 1 FROM matches WHERE match_id IN (SELECT game_id FROM pro_games)")
        == {"matches", "pro_games"},
        "subconsulta no where também conta",
    )

    validate_base(SOLO_OK, "solo")
    validate_base(PRO_OK, "competitivo")
    validate_base(AVISO, "solo")
    validate_base(AVISO, "competitivo")
    validate_base(MISTURA, None)  # sem base não confere nada
    validate_base(MISTURA, "ambos")  # valor desconhecido também não confere
    for sql, base, rotulo in (
        (MISTURA, "solo", "mistura em solo"),
        (MISTURA, "competitivo", "mistura em competitivo"),
        (SOLO_OK, "competitivo", "tabela do solo na base competitivo"),
        (PRO_OK, "solo", "tabela do competitivo na base solo"),
        ("SELECT 1 FROM matches WHERE match_id IN (SELECT game_id FROM pro_games)", "solo", "subconsulta da outra base"),
        ("SELECT 1 FROM matches, pro_games", "solo", "junção por vírgula entre bases"),
    ):
        try:
            validate_base(sql, base)
            falhas.append(f"validate_base devia bloquear: {rotulo}")
        except BaseMixError:
            pass


def cenario(sqls, execucoes):
    chamadas = {"gerar": [], "rodar": []}
    it_sql, it_exec = iter(sqls), iter(execucoes)

    def gerar(question, history=None, model=None, erro_anterior=None, base=None):
        chamadas["gerar"].append({"base": base, "erro_anterior": erro_anterior})
        return next(it_sql)

    def rodar(sql):
        chamadas["rodar"].append(sql)
        r = next(it_exec)
        if isinstance(r, Exception):
            raise r
        return r

    nl_to_sql.generate_sql, nl_to_sql.run_query = gerar, rodar
    return chamadas


def parte2(falhas):
    def confere(cond, msg):
        if not cond:
            falhas.append(msg)

    orig = (nl_to_sql.generate_sql, nl_to_sql.run_query)
    ok = (["n"], [(1,)])
    try:
        c = cenario([PRO_OK], [ok])
        r = nl_to_sql.ask_base("q", base="competitivo")
        confere(r["base"] == "competitivo" and r["tentativas"] == 1, "de primeira, na base competitivo")
        confere(c["gerar"][0]["base"] == "competitivo", "a base devia chegar ao gerador")

        c = cenario([MISTURA, PRO_OK], [ok])
        r = nl_to_sql.ask_base("q", base="competitivo")
        confere(r["tentativas"] == 2 and r["sql"] == PRO_OK, "mistura corrigida na 2a tentativa")
        confere(c["rodar"] == [PRO_OK], "a SQL que mistura bases NÃO pode chegar ao banco")
        ea = c["gerar"][1]["erro_anterior"]
        confere(ea is not None and ea[0] == MISTURA and "outra base" in ea[1],
                "a 2a chamada devia receber a SQL e a mensagem de mistura")
        confere(c["gerar"][1]["base"] == "competitivo", "a 2a chamada mantém a base")

        c = cenario([MISTURA, MISTURA], [])
        try:
            nl_to_sql.ask_base("q", base="solo")
            falhas.append("mistura nas duas tentativas: devia levantar BaseMixError")
        except BaseMixError:
            pass
        confere(c["rodar"] == [], "se as duas misturam, o banco nunca é tocado")

        erro = psycopg2.errors.UndefinedColumn("coluna x nao existe")
        c = cenario(["SELECT x FROM matches", SOLO_OK], [erro, ok])
        r = nl_to_sql.ask_base("q", base="solo")
        confere(r["tentativas"] == 2 and r["base"] == "solo", "erro de banco: refeito uma vez, na mesma base")
        confere(c["gerar"][1]["base"] == "solo", "o erro de banco mantém a base na nova tentativa")

        c = cenario([AVISO], [ok])
        r = nl_to_sql.ask_base("q", base="solo")
        confere(r["tentativas"] == 1, "o aviso de recusa passa na guarda de qualquer base")

        # a correção barrada pela segurança: vale a mistura da primeira
        c = cenario([MISTURA, "DELETE FROM matches"], [])
        try:
            nl_to_sql.ask_base("q", base="solo")
            falhas.append("correção barrada pela validação devia levantar")
        except BaseMixError:
            pass
        confere(c["rodar"] == [], "nada chega ao banco quando a correção é barrada")

        # sem base: comportamento de sempre
        c = cenario([MISTURA], [ok])
        r = nl_to_sql.ask_base("q", base=None)
        confere(r["base"] is None and r["tentativas"] == 1, "sem base não confere mistura")
    finally:
        nl_to_sql.generate_sql, nl_to_sql.run_query = orig


def main() -> int:
    falhas: list[str] = []
    parte1(falhas)
    parte2(falhas)
    print("guarda de base e ask_base")
    for f in falhas:
        print("  FALHA:", f)
    print("OK" if not falhas else f"{len(falhas)} FALHA(S)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
