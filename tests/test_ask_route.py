"""Testa a orquestração de `nl_to_sql.ask` (roteamento + uma ou duas bases).

Sem banco e sem API: `ask_base` e o modelo do roteador são falsos. Confere o que o
plano prometeu (docs/plano_roteamento_nlq.md):

  * pergunta com pista roda UMA base; sem pista, AMBOS, as duas bases;
  * uma base que falha ou é barrada NÃO derruba a outra: o resultado dela traz `erro`;
  * se TODAS falham, levanta a exceção da última (o erro não é engolido);
  * a continuação herda a base do turno anterior; turno AMBOS não herda;
  * cada base só recebe os turnos do histórico que são dela;
  * saída malformada do roteador vira AMBOS;
  * os campos antigos (sql/columns/rows) vêm do primeiro resultado que deu certo.

Uso:  .venv\\Scripts\\python.exe tests\\test_ask_route.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import psycopg2.errors  # noqa: E402

from src.nlq import nl_to_sql  # noqa: E402
from src.nlq.sql_guard import BaseMixError  # noqa: E402

COM_PISTA_SOLO = "Qual o win rate do time azul?"
COM_PISTA_PRO = "Qual equipe venceu mais partidas em 2026?"
SEM_PISTA = "Quantas partidas existem no banco?"


def falso(respostas):
    """respostas: base -> dict com resultado, ou Exception a levantar."""
    chamadas = []

    def ask_base(question, history=None, base=None):
        chamadas.append({"question": question, "history": history, "base": base})
        r = respostas[base]
        if isinstance(r, Exception):
            raise r
        return {"question": question, "base": base, "tentativas": 1, **r}

    ask_base.chamadas = chamadas
    return ask_base


def roteador(texto):
    chamadas = []

    def f(pergunta, base_anterior):
        chamadas.append(base_anterior)
        return texto

    f.chamadas = chamadas
    return f


def res(n):
    return {"sql": f"SELECT {n}", "columns": ["n"], "rows": [(n,)]}


def main() -> int:
    falhas = []

    def confere(cond, msg):
        if not cond:
            falhas.append(msg)

    orig = nl_to_sql.ask_base
    try:
        # 1. pista de solo: uma base
        f = falso({"solo": res(1)})
        nl_to_sql.ask_base = f
        m = roteador("AMBOS")
        r = nl_to_sql.ask(COM_PISTA_SOLO, modelo_roteador=m)
        confere([c["base"] for c in f.chamadas] == ["solo"], "pista de solo devia rodar só o solo")
        confere(r["base"] == "solo" and len(r["resultados"]) == 1, "uma base, um resultado")
        confere(r["roteamento"] == {"classe": "solo", "origem": "regras"}, f"roteamento {r['roteamento']}")
        confere(not m.chamadas, "pista de regra não chama o modelo do roteador")
        confere(r["sql"] == "SELECT 1" and r["rows"] == [(1,)], "campos antigos do primeiro resultado")

        # 2. pista de profissional
        f = falso({"competitivo": res(2)})
        nl_to_sql.ask_base = f
        r = nl_to_sql.ask(COM_PISTA_PRO, modelo_roteador=roteador("AMBOS"))
        confere([c["base"] for c in f.chamadas] == ["competitivo"] and r["base"] == "competitivo",
                "pista de profissional devia rodar só o competitivo")

        # 3. sem pista: AMBOS, as duas bases
        f = falso({"solo": res(1), "competitivo": res(2)})
        nl_to_sql.ask_base = f
        r = nl_to_sql.ask(SEM_PISTA, modelo_roteador=roteador("AMBOS"))
        confere([c["base"] for c in f.chamadas] == ["solo", "competitivo"], "AMBOS devia rodar as duas bases")
        confere([x["base"] for x in r["resultados"]] == ["solo", "competitivo"], "dois resultados rotulados")
        confere(r["base"] == "ambos" and r["roteamento"]["origem"] == "modelo", f"AMBOS: {r['roteamento']}")

        # 4. uma base falha: a outra aparece
        erro = nl_to_sql.SqlExecutionError("SELECT x", psycopg2.errors.UndefinedColumn("sem coluna"))
        f = falso({"solo": res(1), "competitivo": erro})
        nl_to_sql.ask_base = f
        r = nl_to_sql.ask(SEM_PISTA, modelo_roteador=roteador("AMBOS"))
        confere(r["resultados"][0]["erro"] is None and r["resultados"][1]["erro"] is not None,
                "uma base falhou, a outra devia aparecer")
        confere(r["resultados"][1]["erro"]["tipo"] == "execucao" and r["resultados"][1]["erro"]["sql"] == "SELECT x",
                "o erro da base devia trazer tipo e SQL")
        confere(r["sql"] == "SELECT 1", "campos antigos vêm do primeiro que deu certo")

        # 4b. a primeira falha, a segunda dá certo: campos antigos vêm da segunda
        f = falso({"solo": erro, "competitivo": res(2)})
        nl_to_sql.ask_base = f
        r = nl_to_sql.ask(SEM_PISTA, modelo_roteador=roteador("AMBOS"))
        confere(r["sql"] == "SELECT 2" and r["resultados"][0]["erro"] is not None,
                "se a 1a falha, os campos antigos vêm da 2a")

        # 4c. mistura de bases numa delas também não derruba a outra
        f = falso({"solo": BaseMixError("mistura"), "competitivo": res(2)})
        nl_to_sql.ask_base = f
        r = nl_to_sql.ask(SEM_PISTA, modelo_roteador=roteador("AMBOS"))
        confere(r["resultados"][0]["erro"]["tipo"] == "mistura_de_bases", "tipo mistura_de_bases")

        # 5. todas falham: levanta a da última
        f = falso({"solo": erro, "competitivo": ValueError("Tabelas não permitidas")})
        nl_to_sql.ask_base = f
        try:
            nl_to_sql.ask(SEM_PISTA, modelo_roteador=roteador("AMBOS"))
            falhas.append("todas falham: devia levantar")
        except ValueError as exc:
            confere("Tabelas" in str(exc), "levanta a exceção da ÚLTIMA base")
        f = falso({"competitivo": erro})
        nl_to_sql.ask_base = f
        try:
            nl_to_sql.ask(COM_PISTA_PRO, modelo_roteador=roteador("AMBOS"))
            falhas.append("uma base só, falha: devia levantar SqlExecutionError")
        except nl_to_sql.SqlExecutionError as exc:
            confere(exc.sql == "SELECT x", "SqlExecutionError carrega a SQL")

        # 6. histórico: continuação herda a base e cada base só vê os turnos dela
        hist = [{"question": "Qual equipe venceu mais?", "sql": "SELECT 1", "base": "competitivo"}]
        f = falso({"competitivo": res(2)})
        nl_to_sql.ask_base = f
        m = roteador("AMBOS")
        r = nl_to_sql.ask("e em 2025?", hist, modelo_roteador=m)
        confere(r["roteamento"] == {"classe": "competitivo", "origem": "heranca"} and not m.chamadas,
                f"continuação devia herdar: {r['roteamento']}")

        hist2 = [{"question": "q", "sql": "SELECT a", "base": "solo"},
                 {"question": "q", "sql": "SELECT b", "base": "competitivo"}]
        f = falso({"solo": res(1), "competitivo": res(2)})
        nl_to_sql.ask_base = f
        m = roteador("AMBOS")
        r = nl_to_sql.ask("e agora?", hist2, modelo_roteador=m)
        confere(m.chamadas == [None], f"turno AMBOS não herda: o modelo devia ser chamado, {m.chamadas}")
        por_base = {c["base"]: [t["sql"] for t in c["history"]] for c in f.chamadas}
        confere(por_base == {"solo": ["SELECT a"], "competitivo": ["SELECT b"]},
                f"cada base só recebe os turnos dela: {por_base}")

        # histórico sem campo base (versão antiga da tela): vai para todas
        f = falso({"solo": res(1), "competitivo": res(2)})
        nl_to_sql.ask_base = f
        nl_to_sql.ask(SEM_PISTA, [{"question": "x", "sql": "SELECT z"}], modelo_roteador=roteador("AMBOS"))
        confere(all(len(c["history"]) == 1 for c in f.chamadas), "turno sem base vai para as duas")

        # 7. saída ruim do roteador vira AMBOS
        f = falso({"solo": res(1), "competitivo": res(2)})
        nl_to_sql.ask_base = f
        r = nl_to_sql.ask(SEM_PISTA, modelo_roteador=roteador("talvez"))
        confere(r["base"] == "ambos" and r["roteamento"]["origem"] == "padrao" and len(f.chamadas) == 2,
                f"saída ruim: {r['roteamento']}")
    finally:
        nl_to_sql.ask_base = orig

    print("orquestração do ask com roteamento")
    for f_ in falhas:
        print("  FALHA:", f_)
    print("OK" if not falhas else f"{len(falhas)} FALHA(S)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
