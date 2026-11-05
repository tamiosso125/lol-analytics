"""Testa a nova tentativa de `nl_to_sql.ask_base` com falhas SIMULADAS.

Não usa banco nem a API da Anthropic: troca `generate_sql` e `run_query` por
funções falsas. O que se confere é o contrato descrito no docstring de `ask`:

  * funcionou de primeira: 1 tentativa, `generate_sql` chamado uma vez;
  * o banco rejeitou e a correção funciona: 2 tentativas, devolve a SQL corrigida,
    e a segunda chamada recebe a SQL ruim e a mensagem do banco;
  * as duas falham: `SqlExecutionError` com a SQL e a causa da ÚLTIMA tentativa,
    encadeada à primeira (o erro não é engolido);
  * a correção é barrada pela validação de segurança: vale o erro da primeira;
  * estouro de tempo não é refeito;
  * a correção também passa por `validate_sql` (não há atalho para o validador).

Uso:  .venv\\Scripts\\python.exe tests\\test_ask_retry.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import psycopg2.errors  # noqa: E402

from src.nlq import nl_to_sql  # noqa: E402

BOA = "SELECT COUNT(*) FROM matches"
RUIM = "SELECT coluna_que_nao_existe FROM matches"


def cenario(sqls, execucoes):
    """sqls: o que generate_sql devolve em cada chamada; execucoes: por chamada de
    run_query, uma exceção a levantar ou o resultado."""
    chamadas = {"gerar": [], "rodar": []}
    it_sql, it_exec = iter(sqls), iter(execucoes)

    def gerar(question, history=None, model=None, erro_anterior=None, base=None):
        chamadas["gerar"].append(erro_anterior)
        return next(it_sql)

    def rodar(sql):
        chamadas["rodar"].append(sql)
        r = next(it_exec)
        if isinstance(r, Exception):
            raise r
        return r

    nl_to_sql.generate_sql, nl_to_sql.run_query = gerar, rodar
    return chamadas


def main() -> int:
    falhas = []
    orig = (nl_to_sql.generate_sql, nl_to_sql.run_query)

    def confere(cond, msg):
        if not cond:
            falhas.append(msg)

    try:
        c = cenario([BOA], [(["n"], [(1,)])])
        r = nl_to_sql.ask_base("q")
        confere(r["tentativas"] == 1 and len(c["gerar"]) == 1, "de primeira: devia ser 1 tentativa")

        erro = psycopg2.errors.UndefinedColumn("coluna x nao existe")
        c = cenario([RUIM, BOA], [erro, (["n"], [(1,)])])
        r = nl_to_sql.ask_base("q")
        confere(r["tentativas"] == 2 and r["sql"] == BOA, "correcao: devia devolver a SQL corrigida em 2 tentativas")
        confere(c["gerar"][0] is None and c["gerar"][1] is not None, "a 2a chamada devia levar erro_anterior")
        confere(c["gerar"][1][0] == RUIM and "coluna x nao existe" in c["gerar"][1][1],
                "erro_anterior devia ter a SQL ruim e a mensagem do banco")

        e2 = psycopg2.errors.UndefinedColumn("outra falha")
        c = cenario([RUIM, RUIM], [erro, e2])
        try:
            nl_to_sql.ask_base("q")
            confere(False, "as duas falham: devia levantar SqlExecutionError")
        except nl_to_sql.SqlExecutionError as exc:
            confere(exc.sql == RUIM and exc.cause is e2, "SqlExecutionError devia ter a SQL e a causa da ultima tentativa")
            confere(exc.__cause__ is erro, "a primeira falha devia estar encadeada em __cause__")

        c = cenario([RUIM, "DELETE FROM matches"], [erro])
        try:
            nl_to_sql.ask_base("q")
            confere(False, "correcao barrada: devia levantar SqlExecutionError")
        except nl_to_sql.SqlExecutionError as exc:
            confere(exc.sql == RUIM and exc.cause is erro, "correcao barrada: devia valer o erro da primeira SQL")
        confere(len(c["rodar"]) == 1, "correcao barrada pela validacao nao pode chegar ao banco")

        c = cenario([RUIM, "SELECT * FROM pg_user"], [erro])
        try:
            nl_to_sql.ask_base("q")
            confere(False, "correcao com tabela fora da lista: devia levantar")
        except nl_to_sql.SqlExecutionError:
            pass
        confere(len(c["rodar"]) == 1, "a correcao tambem passa por validate_sql")

        lenta = psycopg2.errors.QueryCanceled("statement timeout")
        c = cenario([RUIM], [lenta])
        try:
            nl_to_sql.ask_base("q")
            confere(False, "timeout: devia levantar")
        except nl_to_sql.SqlExecutionError:
            pass
        confere(len(c["gerar"]) == 1, "timeout nao deve ser refeito")
    finally:
        nl_to_sql.generate_sql, nl_to_sql.run_query = orig

    print("7 cenarios")
    for f in falhas:
        print("  FALHA:", f)
    print("OK" if not falhas else f"{len(falhas)} FALHA(S)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
