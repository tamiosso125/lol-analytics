"""Baseline de comparação entre modelos (objetivo específico e do TCC).

Compara Random Forest, XGBoost e rede neural (MLP) na predição de
vitória do time azul aos 15 min, com validação cruzada estratificada.
Métricas: acurácia, precisão, recall, F1 e AUC-ROC
(conforme apontado na ficha de avaliação do TCC I).

Uso:  python -m src.models.train_baseline
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]


def main() -> None:
    df = pd.read_csv("data/features.csv")
    X, y = df[FEATURES], df["blue_win"]
    print(f"{len(df)} partidas | taxa de vitória azul: {y.mean():.3f}")

    models = {
        "RandomForest": RandomForestClassifier(n_estimators=300, random_state=42),
        "XGBoost": XGBClassifier(
            n_estimators=300, learning_rate=0.05, eval_metric="logloss", random_state=42
        ),
        "MLP": make_pipeline(
            StandardScaler(),
            MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42),
        ),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    print(f"\n{'Modelo':<14} {'Acurácia':>10} {'Precisão':>10} {'Recall':>10} {'F1':>10} {'AUC-ROC':>10}")
    for name, model in models.items():
        res = cross_validate(model, X, y, cv=cv, scoring=scoring)
        print(
            f"{name:<14} "
            f"{res['test_accuracy'].mean():>10.4f} "
            f"{res['test_precision'].mean():>10.4f} "
            f"{res['test_recall'].mean():>10.4f} "
            f"{res['test_f1'].mean():>10.4f} "
            f"{res['test_roc_auc'].mean():>10.4f}"
        )


if __name__ == "__main__":
    main()
