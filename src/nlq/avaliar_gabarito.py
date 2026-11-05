"""Compara a saída bruta do sistema com o gabarito (SQL de referência), sem julgamento humano.

Fluxo: `gerar_gabarito` cria perguntas + SQL de referência ANTES de qualquer execução do
sistema; `avaliar_conjunto` roda as perguntas pelo caminho do produto e grava a saída bruta;
este módulo só compara. Regras (todas declaradas aqui, para quem for auditar):

* pergunta com recusa esperada: passa se TODA base consultada recusou
  (`SELECT 'não é possível responder...'`). Se alguma base devolveu número, falhou, mesmo que
  a outra tenha recusado: o usuário veria uma resposta inventada.
* pergunta respondível: precisa de um resultado, na BASE ESPERADA, que bata com o gabarito.
  Resposta só na base errada, recusa, erro de execução ou erro de validação falham.
* escalar: algum valor da primeira linha do resultado bate com o do gabarito
  (tolerância relativa de 0,1%; fração e percentual são aceitos, 0,53 ou 53).
* ranking (top N / "o mais X"): a chave de cada linha do gabarito (primeira coluna)
  aparece, na MESMA posição, entre as células da linha correspondente do sistema.
* colunas extras e ordem das colunas não importam; linhas extras no fim de um ranking não
  importam (o limite pedido já saiu no gabarito).

Uso:
  python -m src.nlq.avaliar_gabarito --resultado reports/a.json [reports/b.json ...] \
      --saida reports/nlq_gabarito_resultado.json
"""
import argparse
import json
import math
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))

GABARITO = RAIZ / "docs" / "nlq_gabarito_900.json"


def e_recusa(res: dict) -> bool:
    return not res.get("erro") and "não é possível responder" in (res.get("sql") or "")


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _igual_num(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-3, abs_tol=1e-4)


def _norm(s) -> str:
    sem = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in sem if not unicodedata.combining(c)).strip().lower()


def bate_escalar(ref_rows: list, rows: list) -> bool:
    if not ref_rows or not rows:
        return False
    alvo = _num(ref_rows[0][-1])
    if alvo is None:
        return any(_norm(c) == _norm(ref_rows[0][-1]) for c in rows[0])
    for c in rows[0]:
        v = _num(c)
        if v is None:
            continue
        # fração × percentual: 0,53 e 53 são a mesma resposta
        if _igual_num(v, alvo) or (abs(alvo) <= 1.0 and _igual_num(v, alvo * 100)):
            return True
    return False


def bate_ranking(ref_rows: list, rows: list) -> bool:
    if not ref_rows or len(rows) < len(ref_rows):
        return False
    for ref, lin in zip(ref_rows, rows):
        chave = _norm(ref[0])
        if not any(_norm(c) == chave for c in lin):
            return False
    return True


def executar_referencia(sql: str) -> list:
    import os

    import psycopg2

    from src import config  # noqa: F401

    c = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        c.set_session(readonly=True)
        cur = c.cursor()
        cur.execute("SET statement_timeout = 30000")
        cur.execute(sql)
        return cur.fetchall()
    finally:
        c.close()


def julgar(item: dict, reg: dict | None, ref_rows: list | None) -> dict:
    """Devolve {passou, motivo} para UMA pergunta."""
    if reg is None:
        return {"passou": False, "motivo": "sem execução do sistema"}
    if reg.get("status") == "erro":
        tipo = (reg.get("erro") or {}).get("tipo", "erro")
        return {"passou": False, "motivo": f"erro do sistema ({tipo})"}
    resultados = reg.get("resultados", [])
    if item["recusa_esperada"]:
        if resultados and all(e_recusa(r) for r in resultados if not r.get("erro")) and \
                any(e_recusa(r) for r in resultados):
            return {"passou": True, "motivo": "recusou, como esperado"}
        return {"passou": False, "motivo": "devolveu resposta onde o banco não tem o dado"}
    da_base = [r for r in resultados if r["base"] == item["base"]]
    if not da_base:
        return {"passou": False, "motivo": f"roteou só para {','.join(r['base'] for r in resultados) or '-'}"}
    r = da_base[0]
    if r.get("erro"):
        return {"passou": False, "motivo": "erro de execução na base esperada"}
    if e_recusa(r):
        return {"passou": False, "motivo": "recusa indevida (o banco tem o dado)"}
    ok = bate_ranking(ref_rows, r["rows"]) if item["tipo"] == "ranking" else bate_escalar(ref_rows, r["rows"])
    return {"passou": ok, "motivo": "confere com o gabarito" if ok else "valor diferente do gabarito"}


def wilson(k: int, n: int, z: float = 1.96) -> list:
    if not n:
        return [0.0, 0.0]
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resultado", nargs="+", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--gabarito", default=str(GABARITO))
    args = ap.parse_args()

    gab = json.loads(Path(args.gabarito).read_text(encoding="utf-8"))["itens"]
    por_id = {}
    sistema = None
    for arq in args.resultado:
        d = json.loads((RAIZ / arq).read_text(encoding="utf-8"))
        sistema = sistema or d.get("sistema")
        for r in d["registros"]:
            por_id[r["n"]] = r

    linhas = []
    for item in gab:
        reg = por_id.get(item["id"])
        ref_rows = None
        if not item["recusa_esperada"] and reg is not None:
            # o gabarito é reexecutado aqui (banco no mesmo estado da rodada)
            ref_rows = executar_referencia(item["sql_ref"])
        j = julgar(item, reg, ref_rows)
        linhas.append({"id": item["id"], "familia": item["familia"], "base": item["base"],
                       "recusa_esperada": item["recusa_esperada"], "pergunta": item["pergunta"],
                       **j,
                       "sql_sistema": next((r.get("sql") for r in (reg or {}).get("resultados", [])
                                            if r["base"] == item["base"]), None)})
    exec_ = [l for l in linhas if l["motivo"] != "sem execução do sistema"]
    k = sum(l["passou"] for l in exec_)

    def agrupar(chave):
        out = {}
        for l in exec_:
            g = out.setdefault(str(l[chave]), [0, 0])
            g[1] += 1
            g[0] += l["passou"]
        return {a: {"certas": x[0], "total": x[1], "pct": round(100 * x[0] / x[1], 1)} for a, x in sorted(out.items())}

    resp = [l for l in exec_ if not l["recusa_esperada"]]
    rec = [l for l in exec_ if l["recusa_esperada"]]
    resumo = {
        "executadas": len(exec_), "certas": k, "pct": round(100 * k / max(len(exec_), 1), 1),
        "wilson95": wilson(k, len(exec_)),
        "respondiveis": {"certas": sum(l["passou"] for l in resp), "total": len(resp)},
        "recusas_esperadas": {"certas": sum(l["passou"] for l in rec), "total": len(rec)},
        "por_base": agrupar("base"), "por_familia": agrupar("familia"),
        "motivos_das_falhas": {m: sum(1 for l in exec_ if not l["passou"] and l["motivo"] == m)
                               for m in sorted({l["motivo"] for l in exec_ if not l["passou"]})},
    }
    Path(RAIZ / args.saida).write_text(json.dumps(
        {"gerado_em": datetime.now().isoformat(timespec="seconds"), "sistema": sistema,
         "resumo": resumo, "itens": linhas}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k_: v for k_, v in resumo.items() if k_ not in ("por_familia",)}, ensure_ascii=False, indent=1))
    print("\npor família (certas/total):")
    for f, x in resumo["por_familia"].items():
        print(f"  {f:<26} {x['certas']:>3}/{x['total']:<3} {x['pct']:>5}%")


if __name__ == "__main__":
    main()
