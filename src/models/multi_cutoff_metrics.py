"""Gera o quadro do Apêndice C: métricas por corte temporal e por modelo.

Por que este script existe: o quadro de 4 cortes × 3 modelos estava no
`tcc2_texto.md` sem comando que o reproduzisse — `train_baseline.py` faz
só o corte de 15 min. Um quadro de resultado sem comando para regerá-lo é
fragilidade evável, e foi registrada como pendência em 2026-10-04.

Diferença deliberada em relação aos scripts de treino: aqui a validação
cruzada usa hiperparâmetros de PRODUÇÃO (500/0,01/3, os que `export_model`
aplica) e NÃO os da base de 10 mil, para que a comparação entre os três
modelos seja feita em igualdade de condições — é o mesmo desenho do quadro
anterior, agora reproduzível.

Uso:  python -m src.models.multi_cutoff_metrics
Gera: imprime o quadro em markdown, pronto para o Apêndice C
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
CUTOFFS = [10, 15, 20, 25]

# Hiperparâmetros de PRODUÇÃO (export_model.py), não os da base de 10 mil.
# Usar os errados aqui compararia modelos em condições desiguais.
PROD = dict(n_estimators=500, learning_rate=0.01, max_depth=3, eval_metric="logloss")


def main() -> None:
    df = pd.read_csv("data/features_phases.csv")
    linhas = []
    for cutoff in CUTOFFS:
        part = df[df["cutoff_min"] == cutoff]
        X, y = part[FEATURES], part["blue_win"]
        n = len(part)
        wr = y.mean()
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        modelos = {
            "RandomForest": RandomForestClassifier(n_estimators=500, random_state=42),
            "XGBoost": XGBClassifier(random_state=42, **PROD),
            "MLP": make_pipeline(StandardScaler(),
                                 MLPClassifier(hidden_layer_sizes=(64, 32),
                                               max_iter=500, random_state=42)),
        }
        for nome, modelo in modelos.items():
            # cross_val_predict devolve as probabilidades fora da amostra, o
            # que permite calcular AUC/F1/precisão/recall sem leakage — o
            # `cross_validate(scoring=...)` de train_baseline também faz, mas
            # aqui precisamos das probabilidades para todas as métricas.
            # AUC-ROC exige as PROBABILIDADES, não a classe prevista: usar
            # `pred` (0/1) mede o poder de ranking de um classificador
            # binário e subestima a área em ~0,09 — erro cometido na primeira
            # versão deste script, que reportava 0,7596 no corte de 15 min
            # onde o correto é 0,8473.
            proba = cross_val_predict(modelo, X, y, cv=cv, method="predict_proba")[:, 1]
            pred = (proba >= 0.5).astype(int)
            bold = "**" if nome == "XGBoost" else ""
            fim = "**" if nome == "XGBoost" else ""
            linhas.append(
                f"| {cutoff}min | {n:,} | {wr:.3f}".replace(",", ".")
                + f" | {bold}{nome}{fim} | {accuracy_score(y, pred):.4f}"
                + f" | {precision_score(y, pred):.4f} | {recall_score(y, pred):.4f}"
                + f" | {f1_score(y, pred):.4f} | {roc_auc_score(y, proba):.4f} |"
            )
    print("| Corte | n | Taxa vitória azul | Modelo | Acurácia | Precisão | "
          "Recall | F1 | AUC-ROC |")
    print("|---|---:|---:|---|---:|---:|---:|---:|---:|")
    for l in linhas:
        print(l)
    print()
    print(f"Base: {len(df):,} linhas em data/features_phases.csv".replace(",", "."))
    print("Hiperparâmetros: PRODUÇÃO (500/0,01/3) para os três modelos, "
          "CV 5-fold estratificada, seed 42.")


if __name__ == "__main__":
    main()