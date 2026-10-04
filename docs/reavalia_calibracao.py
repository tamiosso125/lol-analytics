"""Recalcula o veredito do experimento de calibração a partir do JSON.

POR QUE ESTE SCRIPT: a primeira versão de `experimento_calibracao.py`
declarou "VEREDITO: FECHA" porque o limiar era desvio < 2,0 pp — e a
variante DE PRODUÇÃO já está em 1,7 pp. Ou seja, qualquer coisa que não
fosse pior que a produção contava como "fechou", e o vencedor foi a
RandomForest com 0,6 pp. Melhorar de 1,7 para 1,6 pp — que é o que a
regularização faz — foi contado como sucesso.

Limiar corrigido: para dizer que uma variante FECHA a discrepância, ela
precisa (a) cair abaixo de 1,0 pp de desvio E (b) não custar mais de 0,001
de AUC em relação à produção. Sem (b), trocar de família de modelo para
ganhar 1 ponto de taxa-base às custas de AUC não é uma solução, é uma
troca.

Também registra que o experimento rodou no corte de 15 min, que é o de
MENOR discrepância (1,7 pp). Os outros cortes têm 2,8 / 4,7 / 1,9 pp —
ou seja, o teste rodou no caso mais favorável a "fecha", e ainda assim
não fechou.

Uso:
    .venv\\Scripts\\python.exe docs\\reavalia_calibracao.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "reports" / "experimento_calibracao.json"
DST = RAIZ / "reports" / "experimento_calibracao_veredito.json"

LIMIAR_DESVIO_PP = 1.0   # o que conta como "a discrepância fechou"
LIMIAR_AUC = 0.001       # quanto de AUC se pode perder para fechar


def main() -> None:
    if not SRC.exists():
        sys.exit(f"ERRO: rode antes  python docs/experimento_calibracao.py")
    d = json.loads(SRC.read_text(encoding="utf-8"))
    variantes = [v for v in d["variantes"] if "erro" not in v]
    if not variantes:
        sys.exit("ERRO: nenhuma variante medida")

    prod = variantes[0]
    if not prod["nome"].startswith("producao"):
        sys.exit("ERRO: a primeira variante deveria ser a de produção")

    print("=" * 76)
    print("D1 — REAVALIACAO DO VEREDITO")
    print("=" * 76)
    print(f"corte do experimento : {d['corte_min']} min "
          f"(o de MENOR discrepancia entre os quatro)")
    print(f"referencia dado bruto: {d['referencia_dado_bruto']:.4f}")
    print(f"producao             : AUC {prod['auc']:.4f} | "
          f"taxa-base {prod['taxa_base']:.4f} | desvio {prod['desvio_pp']:.1f} pp")
    print(f"criterio para fechar  : desvio < {LIMIAR_DESVIO_PP} pp E "
          f"custo de AUC < {LIMIAR_AUC}")
    print()

    fecham, pioram = [], []
    for v in variantes[1:]:
        custo_auc = prod["auc"] - v["auc"]          # positivo = perdeu AUC
        fecha = v["desvio_pp"] < LIMIAR_DESVIO_PP and custo_auc < LIMIAR_AUC
        if fecha:
            fecham.append((v, custo_auc))
        elif v["desvio_pp"] > prod["desvio_pp"]:
            pioram.append(v)

    print(f"{'variante':<46}{'desvio':>9}{'d vs prod':>11}{'custo AUC':>11}")
    print("-" * 78)
    for v in variantes[1:]:
        print(f"{v['nome'][:44]:<46}{v['desvio_pp']:>8.1f}pp"
              f"{v['desvio_pp'] - prod['desvio_pp']:>+10.1f}pp"
              f"{prod['auc'] - v['auc']:>+11.4f}")

    print()
    print("=" * 76)
    if fecham:
        for v, custo in fecham:
            print(f"FECHA: {v['nome']} — desvio {v['desvio_pp']:.1f} pp, "
                  f"custo de AUC {custo:+.4f}")
    else:
        print("NENHUMA variante fecha a discrepancia dentro do criterio.")

    if pioram:
        print()
        print("PIORAM a discrepancia:")
        for v in pioram:
            print(f"  {v['nome']:<46}{v['desvio_pp']:>8.1f} pp "
                  f"({v['desvio_pp'] - prod['desvio_pp']:+.1f} pp)")

    # A melhor alternativa, mesmo sem fechar
    melhor = min(variantes[1:], key=lambda v: v["desvio_pp"])
    print()
    print(f"melhor desvio absoluto: {melhor['nome']}")
    print(f"  desvio {melhor['desvio_pp']:.1f} pp "
          f"(producao {prod['desvio_pp']:.1f} pp) | "
          f"AUC {melhor['auc']:.4f} ({melhor['auc'] - prod['auc']:+.4f})")

    print()
    print("VEREDITO CORRIGIDO:")
    if fecham:
        print("  A limitacao da 5.8 TEM solucao de uma linha.")
    else:
        print("  A limitacao da 5.8 NAO tem solucao barata entre as alavancas")
        print("  testadas. E isso ESTRANGE A AFIRMAÇÃO, nao a enfraquece: o texto")
        print("  hoje diz que a GRADE nao achou ajuste melhor. Com este")
        print("  experimento passa a dizer que nem calibracao, nem regularizacao")
        print("  alternativa, nem troca de familia de modelo fecham a")
        print("  discrepancia sem custo — e a calibracao a piora de proposito.")

    saida = {
        "criterio": {"limiar_desvio_pp": LIMIAR_DESVIO_PP,
                     "limiar_custo_auc": LIMIAR_AUC},
        "producao": prod,
        "alguma_variante_fecha": bool(fecham),
        "variantes_que_fecham": [v["nome"] for v, _ in fecham],
        "variantes_que_pioram": [v["nome"] for v in pioram],
        "melhor_desvio": melhor,
    }
    DST.write_text(json.dumps(saida, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(f"\ngravado: {DST}")


if __name__ == "__main__":
    main()