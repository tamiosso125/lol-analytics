"""Métricas completas (acurácia, precisão, recall, F1, AUC-ROC) dos modelos AJUSTADOS aos 15 min.

POR QUE ESTE SCRIPT EXISTE (2026-11-08, parecer do orientador): o Quadro 3
passou a mostrar a comparação após o ajuste de hiperparâmetros e a regressão
logística. `tune_models_full` grava só acurácia e AUC-ROC dos ajustados, e
`baseline_e_diferencas` só acurácia e AUC-ROC da logística; para o quadro
manter precisão, recall e F1, as previsões fora da dobra são refeitas aqui com
as melhores combinações gravadas em `reports/tune_models_39k.json`, no mesmo
protocolo do Quadro 3 (5 dobras estratificadas, semente 42). Acurácia e AUC-ROC
têm de reproduzir os valores já publicados; o script avisa se não reproduzirem.

Uso:
    .venv\\Scripts\\python.exe -m src.models.metricas_ajustados

Grava:
    reports/metricas_ajustados.json
"""
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parents[2]
FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]


def main() -> None:
    df = pd.read_csv(RAIZ / "data" / "features.csv")
    X, y = df[FEATURES], df["blue_win"]
    grade = json.loads((RAIZ / "reports" / "tune_models_39k.json").read_text(encoding="utf-8"))
    rf = grade["RandomForest"]["melhor_combinacao"]
    mlp = {k.split("__")[1]: (tuple(v) if isinstance(v, list) else v)
           for k, v in grade["MLP"]["melhor_combinacao"].items()}
    modelos = {
        # mesma construção de baseline_e_diferencas.py
        "Regressão logística": (make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)), None),
        "Random Forest ajustada": (RandomForestClassifier(random_state=42, **rf), grade["RandomForest"]),
        # mesma construção de tune_models_full.py
        "MLP ajustado": (make_pipeline(StandardScaler(), MLPClassifier(max_iter=1000, random_state=42, **mlp)),
                         grade["MLP"]),
    }
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    saida = {"medido_em": date.today().isoformat(), "partidas": int(len(df)),
             "cv": "StratifiedKFold(5, shuffle=True, random_state=42)", "modelos": {}}
    for nome, (m, ref) in modelos.items():
        p = cross_val_predict(m, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
        pred = (p >= 0.5).astype(int)
        r = {"acuracia": accuracy_score(y, pred), "precisao": precision_score(y, pred),
             "recall": recall_score(y, pred), "f1": f1_score(y, pred), "auc": roc_auc_score(y, p)}
        r = {k: round(float(v), 4) for k, v in r.items()}
        saida["modelos"][nome] = r
        print(nome, r, flush=True)
        if ref and (r["acuracia"], r["auc"]) != (ref["acuracia_quadro3"], ref["auc_quadro3"]):
            print(f"  AVISO: não reproduz tune_models_39k.json ({ref['acuracia_quadro3']}, {ref['auc_quadro3']})")
    (RAIZ / "reports" / "metricas_ajustados.json").write_text(
        json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
    print("gravado: reports/metricas_ajustados.json")


if __name__ == "__main__":
    main()
