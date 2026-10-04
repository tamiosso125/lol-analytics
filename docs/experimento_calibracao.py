"""D1 — testa as duas alavancas que a grade de hiperparâmetros não cobriu.

POR QUE ESTE SCRIPT: a Seção 5.8 sustenta que a limitação de taxa-base NÃO é
subajuste porque a grade escolheu a mesma profundidade e ficou equivalente em
AUC. A afirmação é verdadeira — mas a grade variou só `n_estimators`,
`learning_rate` e `max_depth`. As duas alavancas naturais contra esse
defeito específico nunca foram testadas:

  1. CALIBRAÇÃO. O modelo projeta o empate para perto de 50% quando o dado
     bruto dá 46-48%. Uma calibração isótona ou sigmoidal age exatamente
     sobre esse ponto — remapeia a saída do modelo para a frequência
     observada. Se ela sozinha fechar a discrepância, a limitação da 5.8
     deixa de ser "limitação em aberto".

  2. REGULARIZAÇÃO ALTERNATIVA. `min_child_weight`, `gamma` e `subsample`
     limitam a capacidade do modelo em direções que profundidade e taxa de
     aprendizado não cobrem, e podem empurrar a projeção para longe de 50%
     sem ajuda do ajuste.

O QUE É MEDIDO, e como:
  - AUC-ROC FORA DA AMOSTRA, via `cross_val_predict`. Sem isso, comparar
    variantes que mudam a capacidade do modelo usando número in-sample seria
    exactamente o tipo de erro que a 5.8Commitment de não ser subajuste
    tenta evitar.
  - TAXA-BASE, com o estimador ajustado na base inteira e previsto sobre o
    estado vazio `{}`. É o mesmo procedimento de
    `tests/validate_predictions.py`, então o número é comparável ao da 5.8.
  - A referência é o dado bruto: 47,9% de vitória do azul aos 15 min entre
    partidas empatadas (`reports/taxa_base_por_corte.json`).

Uso:
    .venv\\Scripts\\python.exe docs\\experimento_calibracao.py

Grava:
    reports/experimento_calibracao.json
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from xgboost import XGBClassifier

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

RAIZ = Path(__file__).resolve().parent.parent
FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
CUTOFF = 15
PRODUCAO = dict(n_estimators=500, learning_rate=0.01, max_depth=3)

# Referencia do dado BRUTO, de reports/taxa_base_por_corte.json. Nao hardcoded
# por preferencia: lido do artefato, para que a comparacao nao possa divergir
# se o dado for remedido.
def referencia_bruta() -> float:
    p = RAIZ / "reports" / "taxa_base_por_corte.json"
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))["bruto"][str(CUTOFF)]
        return float(d[2])
    return 0.4788  # ultimo valor medido, se o artefato nao existir


def base_de(estimador, X, y) -> tuple[float, float, float]:
    """AUC fora da amostra e taxa-base no estado vazio.

    Devolve (auc, base, acuracia). O estado vazio e as cinco features
    zeradas — a definicao de "tudo empatado". Um dict solto nao serve:
    o XGBoost recusa (`Not supported type for data`), entao o estado vira
    DataFrame com as colunas na ordem de FEATURES.
    """
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba = cross_val_predict(estimador, X, y, cv=cv, method="predict_proba")[:, 1]
    auc = roc_auc_score(y, proba)
    acur = accuracy_score(y, (proba >= 0.5).astype(int))

    ajustado = estimador
    ajustado.fit(X, y)
    vazio = pd.DataFrame([[0.0] * len(FEATURES)], columns=FEATURES)
    base = float(ajustado.predict_proba(vazio)[0, 1])
    return auc, base, acur


def main() -> None:
    df = pd.read_csv(RAIZ / "data" / "features.csv")
    X, y = df[FEATURES], df["blue_win"]
    ref = referencia_bruta()

    print("=" * 76)
    print(f"D1 — CALIBRACAO E REGULARIZACAO ALTERNATIVA (corte de {CUTOFF} min)")
    print("=" * 76)
    print(f"linhas            : {len(df)}")
    print(f"taxa azul na base : {y.mean():.4f}")
    print(f"referencia BRUTA  : {ref:.4f}  (dado, entre partidas empatadas)")
    print(f"producao          : {PRODUCAO}")
    print("")

    xgb = lambda **kw: XGBClassifier(eval_metric="logloss", random_state=42,
                                      **{**PRODUCAO, **kw})
    variantes = [
        ("producao (sem calibracao)", xgb(), False),
        ("calibrada sigmoidal", xgb(), "sigmoid"),
        ("calibrada isotonica", xgb(), "isotonic"),
        ("regularizada min_child_weight=20", xgb(min_child_weight=20), False),
        ("regularizada gamma=1, subsample=0.8", xgb(gamma=1.0, subsample=0.8), False),
        ("regularizada forte (as duas)",
         xgb(min_child_weight=20, gamma=1.0, subsample=0.8), False),
        ("calib. sigmoidal + regularizacao",
         xgb(min_child_weight=20, gamma=1.0, subsample=0.8), "sigmoid"),
        ("RandomForest 500/prof6 (referencia de capacidade)", 
         RandomForestClassifier(n_estimators=500, max_depth=6, random_state=42), False),
    ]

    print(f"{'variante':<48}{'AUC':>8}{'base':>8}{'|base-bruta|':>14}{'acur':>8}")
    print("-" * 86)
    linhas = []
    for nome, est, metodo in variantes:
        if metodo:
            est = CalibratedClassifierCV(est, method=metodo, cv=5)
        try:
            auc, base, acur = base_de(est, X, y)
        except Exception as exc:  # noqa: BLE001
            print(f"{nome:<48}FALHOU: {type(exc).__name__}")
            linhas.append({"nome": nome, "erro": str(exc)[:80]})
            continue
        desvio = abs(base - ref) * 100
        print(f"{nome:<48}{auc:>8.4f}{base:>8.4f}{desvio:>13.1f}pp{acur:>8.4f}")
        linhas.append({"nome": nome, "auc": round(auc, 4),
                       "taxa_base": round(base, 4),
                       "desvio_pp": round(desvio, 1),
                       "acuracia": round(acur, 4)})

    # --- leitura -------------------------------------------------------
    prod = next((l for l in linhas if l.get("nome", "").startswith("producao")), None)
    print()
    print("=" * 76)
    print("LEITURA PARA A SECAO 5.8")
    print("=" * 76)
    if not prod:
        print("A variante de producao falhou; nada a concluir.")
        return
    print(f"producao            : AUC {prod['auc']:.4f} | base {prod['taxa_base']:.4f} "
          f"| desvio {prod['desvio_pp']:.1f} pp")
    base_prod = prod["taxa_base"]

    fecham = [l for l in linhas
              if l.get("nome") != prod["nome"] and l.get("desvio_pp", 99) < 2.0]
    if fecham:
        print()
        print("Variantes que FECHAM a discrepancia (desvio < 2,0 pp):")
        for l in fecham:
            print(f"  {l['nome']:<48}desvio {l['desvio_pp']:.1f} pp | "
                  f"AUC {l['auc']:.4f} ({l['auc'] - prod['auc']:+.4f})")
        melhor = min(fecham, key=lambda l: l["desvio_pp"])
        ganho = melhor["auc"] - prod["auc"]
        print()
        print(f"VEREDITO: FECHA. {melhor['nome']} reduz o desvio de "
              f"{prod['desvio_pp']:.1f} para {melhor['desvio_pp']:.1f} pp,")
        print(f"          com AUC {melhor['auc']:.4f} ({ganho:+.4f} em relacao a producao).")
        print("          A limitacao da 5.8 deixa de ser em aberto e passa a ter")
        print("          solucao de uma linha.")
    else:
        print()
        print("VEREDITO: NAO FECHA. Nenhuma variante bringing o desvio abaixo de")
        print("          2,0 pp. A limitacao da 5.8 permanece em aberto, e o texto")
        print("          deve dizer que as duas alavancas foram testadas e nao")
        print("          resolveram — em vez de dizer apenas que a grade nao achou.")

    destino = RAIZ / "reports" / "experimento_calibracao.json"
    destino.write_text(json.dumps({
        "medido_em": date.today().isoformat(),
        "corte_min": CUTOFF,
        "linhas": int(len(df)),
        "referencia_dado_bruto": round(ref, 4),
        "producao": PRODUCAO,
        "variantes": linhas,
        "alguma_variante_fecha": bool(fecham),
        "limiar_pp": 2.0,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\ngravado: {destino}")


if __name__ == "__main__":
    main()