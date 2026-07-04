"""Explicabilidade do modelo com SHAP (seção 2.3 do TCC —
García-Méndez e Arriba-Pérez, 2025).

Treina o XGBoost na base de features e gera gráficos SHAP
(importância global e beeswarm) em reports/.

Uso:  python -m src.models.explain_shap
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import shap
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from src.features.build_features import CUTOFF_MIN  # noqa: F401 (documenta o corte)

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]


def main() -> None:
    df = pd.read_csv("data/features.csv")
    X, y = df[FEATURES], df["blue_win"]
    X_tr, X_te, y_tr, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # hiperparâmetros vindos do tuning (src/models/tune_models.py)
    model = XGBClassifier(n_estimators=300, learning_rate=0.01, max_depth=3, eval_metric="logloss")
    model.fit(X_tr, y_tr)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_te)

    os.makedirs("reports", exist_ok=True)
    shap.plots.bar(shap_values, show=False)
    plt.tight_layout()
    plt.savefig("reports/shap_importance.png", dpi=150)
    plt.close()

    shap.plots.beeswarm(shap_values, show=False)
    plt.tight_layout()
    plt.savefig("reports/shap_beeswarm.png", dpi=150)
    plt.close()
    print("Gráficos salvos em reports/shap_importance.png e reports/shap_beeswarm.png")


if __name__ == "__main__":
    main()
