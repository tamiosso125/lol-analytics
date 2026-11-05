"""Contrato do endpoint /ask depois do roteamento (sem banco e sem API da Anthropic).

`ask` da API é trocado por uma função falsa. Confere:
  * a resposta traz `roteamento`, `base` e `resultados` (um por base);
  * cada resultado é cortado em 100 linhas e a falha de uma base aparece em `erro`;
  * os campos antigos (sql/columns/rows/tentativas) continuam lá;
  * a base do histórico chega ao `ask`;
  * SqlExecutionError e BaseMixError continuam virando 422 e 400.

Uso:  .venv\\Scripts\\python.exe tests\\test_api_ask.py
"""
import sys
import warnings
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
warnings.filterwarnings("ignore")

from fastapi.testclient import TestClient  # noqa: E402

from src.api import main  # noqa: E402
from src.nlq.nl_to_sql import SqlExecutionError  # noqa: E402
from src.nlq.sql_guard import BaseMixError  # noqa: E402


def main_teste() -> int:
    falhas = []

    def confere(cond, msg):
        if not cond:
            falhas.append(msg)

    cliente = TestClient(main.app)
    orig = main.ask
    visto = {}
    try:
        def ask_ambos(question, history=None):
            visto["history"] = history
            solo = {"base": "solo", "sql": "SELECT n FROM matches", "columns": ["n"],
                    "rows": [(i,) for i in range(250)], "tentativas": 1, "erro": None}
            pro = {"base": "competitivo", "sql": "SELECT x", "columns": [], "rows": [],
                   "tentativas": None,
                   "erro": {"tipo": "execucao", "message": "falhou", "sql": "SELECT x", "cause": "sem coluna"}}
            return {"question": question, "roteamento": {"classe": "ambos", "origem": "modelo"},
                    "base": "ambos", "resultados": [solo, pro],
                    "sql": solo["sql"], "columns": solo["columns"], "rows": solo["rows"], "tentativas": 1}

        main.ask = ask_ambos
        r = cliente.post("/ask", json={"question": "q", "history": [
            {"question": "a", "sql": "SELECT 1", "base": "solo"}, {"question": "b", "sql": "SELECT 2"}]})
        confere(r.status_code == 200, f"status {r.status_code}")
        j = r.json()
        confere(j["base"] == "ambos" and j["roteamento"] == {"classe": "ambos", "origem": "modelo"}, "roteamento")
        confere([x["base"] for x in j["resultados"]] == ["solo", "competitivo"], "um resultado por base")
        confere(len(j["resultados"][0]["rows"]) == 100 and len(j["rows"]) == 100, "corte de 100 linhas")
        confere(j["resultados"][1]["erro"]["message"] == "falhou" and j["resultados"][0]["erro"] is None,
                "erro de uma base aparece só nela")
        confere(j["sql"] == "SELECT n FROM matches" and j["tentativas"] == 1, "campos antigos continuam")
        confere(visto["history"][0]["base"] == "solo" and visto["history"][1]["base"] is None,
                f"base do histórico chega ao ask: {visto['history']}")

        main.ask = lambda q, h=None: (_ for _ in ()).throw(SqlExecutionError("SELECT x", RuntimeError("boom")))
        r = cliente.post("/ask", json={"question": "q"})
        confere(r.status_code == 422 and r.json()["detail"]["sql"] == "SELECT x", f"422 esperado: {r.status_code}")

        main.ask = lambda q, h=None: (_ for _ in ()).throw(BaseMixError("mistura"))
        r = cliente.post("/ask", json={"question": "q"})
        confere(r.status_code == 400 and "mistura" in str(r.json()["detail"]), f"400 esperado: {r.status_code}")
    finally:
        main.ask = orig

    print("contrato do /ask")
    for f in falhas:
        print("  FALHA:", f)
    print("OK" if not falhas else f"{len(falhas)} FALHA(S)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main_teste())
