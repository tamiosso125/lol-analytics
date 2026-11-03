"""Robustez do número de dobras: 5 (usado no trabalho) contra 10 (Kohavi, 1995).

Por que este script existe: o TCC usa validação cruzada estratificada de 5
dobras, e o artigo que ele cita (Kohavi) recomenda 10. A pergunta da banca é
se isso muda o resultado. Aqui as duas são medidas sobre os MESMOS dados e os
MESMOS modelos de `multi_cutoff_metrics.py` (XGBoost de produção, Random
Forest e MLP de referência), com a mesma semente.

Uso:  python -m src.models.robustez_dobras
Gera: imprime o quadro e grava reports/robustez_dobras.json.
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
PROD = dict(n_estimators=500, learning_rate=0.01, max_depth=3, eval_metric="logloss")


def modelos() -> dict:
    return {
        "XGBoost": XGBClassifier(random_state=42, **PROD),
        "RandomForest": RandomForestClassifier(n_estimators=500, random_state=42, n_jobs=-1),
        "MLP": make_pipeline(StandardScaler(),
                             MLPClassifier(hidden_layer_sizes=(64, 32),
                                           max_iter=500, random_state=42)),
    }


def medir(X, y, dobras: int, modelo) -> tuple[float, float]:
    cv = StratifiedKFold(n_splits=dobras, shuffle=True, random_state=42)
    proba = cross_val_predict(modelo, X, y, cv=cv, method="predict_proba")[:, 1]
    return accuracy_score(y, (proba >= 0.5).astype(int)), roc_auc_score(y, proba)


def main() -> None:
    df = pd.read_csv("data/features_phases.csv")
    saida: dict = {}
    linhas = []
    # XGBoost nos quatro cortes; os três modelos no corte de 15 min
    for corte in (10, 15, 20, 25):
        parte = df[df["cutoff_min"] == corte]
        X, y = parte[FEATURES], parte["blue_win"]
        for nome, modelo in modelos().items():
            if corte != 15 and nome != "XGBoost":
                continue
            r = {}
            for k in (5, 10):
                acc, auc = medir(X, y, k, modelo)
                r[str(k)] = {"acuracia": round(float(acc), 4), "auc": round(float(auc), 4)}
            saida.setdefault(str(corte), {})[nome] = r
            linhas.append(
                f"| {corte} min | {nome} | {r['5']['acuracia']:.4f} | {r['10']['acuracia']:.4f} "
                f"| {r['5']['auc']:.4f} | {r['10']['auc']:.4f} |"
            )
            print(linhas[-1], flush=True)
    print("\n| Corte | Modelo | Acurácia 5 | Acurácia 10 | AUC 5 | AUC 10 |")
    destino = Path("reports") / "robustez_dobras.json"
    destino.write_text(json.dumps({
        "gerado_em": date.today().isoformat(),
        "base_linhas": int(len(df)),
        "cv": "estratificada, seed 42, 5 e 10 dobras",
        "resultados": saida,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Artefato JSON: {destino}")


if __name__ == "__main__":
    main()
