"""Curva de aprendizado com teste FIXO e os quatro cortes sobre as MESMAS partidas.

POR QUE ESTE SCRIPT EXISTE (2026-11-08, parecer do orientador): duas leituras
do texto misturavam efeitos.

1. Volume. A sequência 0,8214 -> 0,8393 -> 0,8490 de AUC-ROC aos 15 min vem de
   três rodadas de coleta (10.295, 23.133 e 40.816 partidas), cada uma com seu
   próprio conjunto de teste. Mudaram juntos o tamanho do treino, as partidas
   avaliadas e a composição por região e versão do jogo. Para atribuir o ganho
   ao volume, o teste precisa ser fixo: aqui 20% das partidas (estratificado,
   semente 42) ficam de fora, e o treino cresce dentro dos 80% restantes,
   com 5 sorteios por tamanho.

2. Tempo de jogo. O Quadro 4 avalia cada corte nas partidas que chegam a ele
   (40.816 aos 15 min, 27.761 aos 25). As partidas curtas, que só entram nos
   primeiros cortes, tendem a ser decididas cedo. Aqui os quatro cortes são
   medidos também sobre o mesmo conjunto: as partidas que chegam aos 25 min.

Uso:
    .venv\\Scripts\\python.exe -m src.models.curva_aprendizado

Grava:
    reports/curva_aprendizado.json
"""
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from xgboost import XGBClassifier

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parents[2]
FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
TAMANHOS = (2500, 5000, 10000, 20000)
SORTEIOS = 5


def xgb() -> XGBClassifier:
    return XGBClassifier(n_estimators=500, learning_rate=0.01, max_depth=3,
                         eval_metric="logloss", random_state=42, n_jobs=4)


def oof_auc(d: pd.DataFrame) -> float:
    p = cross_val_predict(xgb(), d[FEATURES], d["blue_win"],
                          cv=StratifiedKFold(5, shuffle=True, random_state=42), method="predict_proba")[:, 1]
    return float(roc_auc_score(d["blue_win"], p))


def main() -> None:
    df = pd.read_csv(RAIZ / "data" / "features_phases.csv")
    saida = {"medido_em": date.today().isoformat()}

    d15 = df[df.cutoff_min == 15].reset_index(drop=True)
    tr, te = train_test_split(d15, test_size=0.2, stratify=d15["blue_win"], random_state=42)
    print(f"(1) curva de aprendizado aos 15 min: teste fixo de {len(te)} partidas", flush=True)
    curva = []
    for n in (*TAMANHOS, len(tr)):
        aucs = []
        for s in range(SORTEIOS if n < len(tr) else 1):
            sub = tr.sample(n=n, random_state=s) if n < len(tr) else tr
            m = xgb().fit(sub[FEATURES], sub["blue_win"])
            aucs.append(roc_auc_score(te["blue_win"], m.predict_proba(te[FEATURES])[:, 1]))
        curva.append({"treino": int(n), "auc_media": round(float(np.mean(aucs)), 4),
                      "auc_dp": round(float(np.std(aucs)), 4), "sorteios": len(aucs)})
        print(f"    treino {n:>6}: AUC-ROC {np.mean(aucs):.4f} (dp {np.std(aucs):.4f})", flush=True)
    saida["curva_15min"] = {"teste_fixo": int(len(te)), "treino_maximo": int(len(tr)),
                            "divisao": "train_test_split(test_size=0.2, stratify, random_state=42)",
                            "pontos": curva}

    ids25 = set(df.loc[df.cutoff_min == 25, "match_id"])
    print(f"\n(2) AUC-ROC por corte (5 dobras, semente 42)", flush=True)
    cortes = {}
    for c in (10, 15, 20, 25):
        elegiveis = df[df.cutoff_min == c].reset_index(drop=True)
        mesmas = elegiveis[elegiveis.match_id.isin(ids25)].reset_index(drop=True)
        a_el, a_mesmas = oof_auc(elegiveis), oof_auc(mesmas)
        cortes[str(c)] = {"elegiveis_n": int(len(elegiveis)), "elegiveis_auc": round(a_el, 4),
                          "mesmas_n": int(len(mesmas)), "mesmas_auc": round(a_mesmas, 4)}
        print(f"    {c} min: elegíveis {len(elegiveis)} -> {a_el:.4f} | mesmas {len(mesmas)} -> {a_mesmas:.4f}",
              flush=True)
    saida["cortes"] = cortes

    destino = RAIZ / "reports" / "curva_aprendizado.json"
    destino.write_text(json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"gravado: {destino}")


if __name__ == "__main__":
    main()
