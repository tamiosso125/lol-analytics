"""Modelo de predição para o COMPETITIVO aos 15 min + comparação formal
com o solo queue (planejamento v2, sprint 2).

Pergunta de pesquisa: o jogo profissional é mais previsível a partir do
MESMO estado de partida? A página Competitivo já mostra que o pro
converte vantagem de ouro melhor; aqui a comparação é formal: o mesmo
classificador (XGBoost com os hiperparâmetros tunados de produção),
avaliado por validação cruzada estratificada, sobre:

  - features COMPARTILHADAS aos 15 min (existem nos dois datasets):
    gold_diff, xp_diff, kill_diff — a comparação justa;
  - o conjunto completo de cada dataset como contexto (solo: +towers/
    dragons; pro: +cs_diff).

Também salva data/model_pro.joblib (XGBoost nas 3 features
compartilhadas, treinado em todos os anos do pro) — insumo do futuro
"pro ao vivo" (planejamento v2, passo 4), em que o feed de livestats
fornece exatamente ouro/XP/abates.

Uso:  python -m src.models.train_pro
"""
import joblib
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from xgboost import XGBClassifier

from src.db import get_conn

SHARED = ["gold_diff", "xp_diff", "kill_diff"]
SOLO_FULL = SHARED + ["tower_diff", "dragon_diff"]
PRO_FULL = SHARED + ["cs_diff"]


def model() -> XGBClassifier:
    # mesmos hiperparâmetros tunados usados em produção (export_model)
    return XGBClassifier(
        n_estimators=500, learning_rate=0.01, max_depth=3,
        eval_metric="logloss", random_state=42,
    )


def evaluate(name: str, X: pd.DataFrame, y: pd.Series) -> None:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    res = cross_validate(model(), X, y, cv=cv, scoring=["accuracy", "roc_auc"])
    print(
        f"{name:<42} n={len(y):>6}  "
        f"acc={res['test_accuracy'].mean():.4f}  "
        f"auc={res['test_roc_auc'].mean():.4f}"
    )


def main() -> None:
    with get_conn() as conn:
        pro = pd.read_sql(
            """SELECT year, win::int AS win,
                      gold_diff_at15 AS gold_diff, xp_diff_at15 AS xp_diff,
                      kill_diff_at15 AS kill_diff, cs_diff_at15 AS cs_diff
               FROM pro_games
               WHERE side = 'Blue'
                 AND gold_diff_at15 IS NOT NULL AND xp_diff_at15 IS NOT NULL
                 AND kill_diff_at15 IS NOT NULL AND cs_diff_at15 IS NOT NULL""",
            conn,
        )
    solo = pd.read_csv("data/features.csv")  # corte de 15 min

    print("Comparação formal solo queue × competitivo (XGBoost tunado, CV 5-fold)\n")
    print("--- features compartilhadas aos 15 min (gold/xp/kill diff) ---")
    evaluate("solo queue (Challenger/GM BR)", solo[SHARED], solo["blue_win"])
    evaluate("competitivo (todos os anos)", pro[SHARED], pro["win"])
    modern = pro[pro.year >= 2023]
    evaluate("competitivo (2023+, era moderna)", modern[SHARED], modern["win"])

    print("\n--- conjunto completo de cada dataset (contexto) ---")
    evaluate("solo queue, 5 features", solo[SOLO_FULL], solo["blue_win"])
    evaluate("competitivo, +cs_diff", pro[PRO_FULL], pro["win"])

    final = model()
    final.fit(pro[SHARED], pro["win"])
    joblib.dump(final, "data/model_pro.joblib")
    print("\nModelo pro (3 features compartilhadas, todos os anos) -> data/model_pro.joblib")


if __name__ == "__main__":
    main()
