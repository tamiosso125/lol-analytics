"""Tuning de hiperparâmetros e curva de calibração (etapa 4 do TCC II).

Busca em grade (GridSearchCV) para os 3 modelos, com a mesma validação
cruzada estratificada de train_baseline.py. Reporta as 5 métricas com os
melhores hiperparâmetros de cada modelo e gera uma curva de calibração
comparando os 3 em reports/.

Uso:  python -m src.models.tune_models
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]

PARAM_GRIDS = {
    "RandomForest": (
        RandomForestClassifier(random_state=42),
        {
            "n_estimators": [200, 300, 500],
            "max_depth": [None, 6, 10],
            "min_samples_leaf": [1, 2, 5],
        },
    ),
    "XGBoost": (
        XGBClassifier(eval_metric="logloss", random_state=42),
        {
            "n_estimators": [200, 300, 500],
            "learning_rate": [0.01, 0.05, 0.1],
            "max_depth": [3, 4, 6],
        },
    ),
    "MLP": (
        make_pipeline(StandardScaler(), MLPClassifier(max_iter=1000, random_state=42)),
        {
            "mlpclassifier__hidden_layer_sizes": [(32,), (64, 32), (128, 64)],
            "mlpclassifier__alpha": [0.0001, 0.001, 0.01],
        },
    ),
}


def main() -> None:
    df = pd.read_csv("data/features.csv")
    X, y = df[FEATURES], df["blue_win"]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]

    print(f"{len(df)} partidas | taxa de vitória azul: {y.mean():.3f}\n")
    print(f"{'Modelo':<14} {'Acurácia':>10} {'Precisão':>10} {'Recall':>10} {'F1':>10} {'AUC-ROC':>10}")

    best_models = {}
    for name, (estimator, grid) in PARAM_GRIDS.items():
        search = GridSearchCV(estimator, grid, scoring="roc_auc", cv=cv, n_jobs=-1)
        search.fit(X, y)
        best_models[name] = search.best_estimator_

        res = cross_validate(search.best_estimator_, X, y, cv=cv, scoring=scoring)
        print(
            f"{name:<14} "
            f"{res['test_accuracy'].mean():>10.4f} "
            f"{res['test_precision'].mean():>10.4f} "
            f"{res['test_recall'].mean():>10.4f} "
            f"{res['test_f1'].mean():>10.4f} "
            f"{res['test_roc_auc'].mean():>10.4f}"
        )
        print(f"  melhores parâmetros: {search.best_params_}")

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    os.makedirs("reports", exist_ok=True)
    plt.figure(figsize=(6, 6))
    plt.plot([0, 1], [0, 1], "k--", label="Perfeitamente calibrado")
    for name, model in best_models.items():
        model.fit(X_tr, y_tr)
        proba = model.predict_proba(X_te)[:, 1]
        frac_pos, mean_pred = calibration_curve(y_te, proba, n_bins=10)
        plt.plot(mean_pred, frac_pos, marker="o", label=name)
    plt.xlabel("Probabilidade prevista média")
    plt.ylabel("Fração de positivos")
    plt.title("Curva de calibração")
    plt.legend()
    plt.tight_layout()
    plt.savefig("reports/calibration_curve.png", dpi=150)
    plt.close()
    print("\nCurva de calibração salva em reports/calibration_curve.png")


if __name__ == "__main__":
    main()
