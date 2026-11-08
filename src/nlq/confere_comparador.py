"""Quantos acertos escalares do gabarito dependem da regra "qualquer valor da 1ª linha".

POR QUE ESTE SCRIPT EXISTE (2026-11-08, parecer do orientador): em pergunta
escalar, `avaliar_gabarito.bate_escalar` aceita a resposta se QUALQUER valor
numérico da primeira linha do sistema bater com o número de referência. Se o
sistema devolver várias colunas numéricas, essa regra pode aceitar por
coincidência. Aqui se mede, na rodada que deu 181 de 203, quantos acertos
escalares tinham mais de uma coluna numérica na primeira linha (os únicos em
que a regra branda poderia decidir).

Reexecuta a SQL gravada do sistema e a de referência, em transação somente
leitura, sobre a base congelada. Nenhuma chamada à API do modelo.

Uso:
    .venv\\Scripts\\python.exe -m src.nlq.confere_comparador

Grava:
    reports/nlq_comparador_ambiguidade.json
"""
import json
import sys
from datetime import date
from pathlib import Path

from src.nlq.avaliar_gabarito import _igual_num, _num, executar_referencia

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parents[2]


def main() -> None:
    gab = {i["id"]: i for i in json.loads((RAIZ / "docs" / "nlq_gabarito_203.json").read_text(encoding="utf-8"))["itens"]}
    res = json.loads((RAIZ / "reports" / "nlq_gabarito_resultado_203.json").read_text(encoding="utf-8"))["itens"]
    acertos = [r for r in res if r["passou"] and not r["recusa_esperada"]]
    escalares = [r for r in acertos if gab[r["id"]]["tipo"] == "escalar"]
    ambiguos, falhas = [], []
    for r in escalares:
        ref = executar_referencia(gab[r["id"]]["sql_ref"])
        try:
            sis = executar_referencia(r["sql_sistema"])
        except Exception as e:  # noqa: BLE001
            falhas.append({"id": r["id"], "erro": type(e).__name__})
            continue
        alvo = _num(ref[0][-1])
        linha = sis[0] if sis else []
        numericas = [i for i, c in enumerate(linha) if _num(c) is not None]
        if len(numericas) >= 2:
            batem = [i for i in numericas if alvo is not None and (
                _igual_num(_num(linha[i]), alvo) or (abs(alvo) <= 1 and _igual_num(_num(linha[i]), alvo * 100)))]
            ambiguos.append({"id": r["id"], "familia": gab[r["id"]]["familia"], "colunas": len(linha),
                             "numericas": len(numericas), "colunas_que_batem": batem})
    saida = {"medido_em": date.today().isoformat(), "rodada": "reports/nlq_gabarito_resultado_203.json",
             "acertos_respondiveis": len(acertos), "acertos_escalares": len(escalares),
             "acertos_ranking": sum(1 for r in acertos if gab[r["id"]]["tipo"] == "ranking"),
             "escalares_com_2_ou_mais_colunas_numericas": len(ambiguos), "casos": ambiguos,
             "falhas_ao_reexecutar": falhas}
    print(json.dumps({k: v for k, v in saida.items() if k != "casos"}, ensure_ascii=False, indent=1))
    (RAIZ / "reports" / "nlq_comparador_ambiguidade.json").write_text(
        json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
    print("gravado: reports/nlq_comparador_ambiguidade.json")


if __name__ == "__main__":
    main()
