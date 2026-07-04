"""Exporta os modelos de produção para a API (endpoint /predict).

Treina um XGBoost com os hiperparâmetros tunados (src/models/tune_models.py)
para CADA corte de tempo (10/15/20/25 min — fases do jogo) na base
data/features_phases.csv e salva:
  - data/models_phases.joblib          ({corte: modelo} para a API)
  - data/model.joblib                  (modelo do corte de 15 — compat.)
  - reports/shap_importance.json       (importância |SHAP| no corte de 15)
  - reports/shap_importance_phases.json ({corte: {feature: importância}})

Uso:  python -m src.models.export_model
"""
import json
import os

import joblib
import pandas as pd
import shap
from xgboost import XGBClassifier

from src.features.build_features import CUTOFFS

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]


def main() -> None:
    df = pd.read_csv("data/features_phases.csv")
    models: dict[int, XGBClassifier] = {}
    importance_phases: dict[str, dict[str, float]] = {}

    for cutoff in CUTOFFS:
        part = df[df["cutoff_min"] == cutoff]
        X, y = part[FEATURES], part["blue_win"]
        # hiperparâmetros vindos do tuning (src/models/tune_models.py,
        # rerodado no dataset de 10k em 2026-07-03: n_estimators subiu
        # de 300 para 500 com a base maior)
        model = XGBClassifier(
            n_estimators=500, learning_rate=0.01, max_depth=3,
            eval_metric="logloss", random_state=42,
        )
        model.fit(X, y)
        models[cutoff] = model

        explainer = shap.TreeExplainer(model)
        shap_values = explainer(X)
        importance_phases[str(cutoff)] = {
            feat: float(abs(shap_values.values[:, i]).mean())
            for i, feat in enumerate(FEATURES)
        }
        print(f"corte {cutoff} min: {len(part)} partidas")

    joblib.dump(models, "data/models_phases.joblib")
    joblib.dump(models[15], "data/model.joblib")
    os.makedirs("reports", exist_ok=True)
    with open("reports/shap_importance_phases.json", "w", encoding="utf-8") as f:
        json.dump(importance_phases, f, indent=2)
    with open("reports/shap_importance.json", "w", encoding="utf-8") as f:
        json.dump(importance_phases["15"], f, indent=2)
    print("Modelos -> data/models_phases.joblib (+ model.joblib do corte 15)")
    print("Importância SHAP -> reports/shap_importance*.json")


if __name__ == "__main__":
    main()
