"""Baseline simples e intervalo de confiança da diferença entre os modelos.

Por que este script existe: o TCC diz que XGBoost, Random Forest e MLP
empatam tecnicamente ("diferenças de milésimos"), mas isso nunca foi testado,
e o único baseline era "sempre vermelho" (53,4%). Aqui:

  1. uma regressão logística (variáveis padronizadas) entra como baseline
     simples, nos quatro cortes;
  2. a diferença de AUC-ROC e de acurácia entre o XGBoost e cada outro
     modelo recebe um intervalo de 95% por *bootstrap* PAREADO: as mesmas
     partidas sorteadas para os dois modelos, sobre as previsões fora da
     amostra da validação cruzada (5 dobras, semente 42, como no Quadro 3).

Uso:  python -m src.models.baseline_e_diferencas
Gera: imprime os quadros e grava reports/baseline_e_diferencas.json.
"""
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
PROD = dict(n_estimators=500, learning_rate=0.01, max_depth=3, eval_metric="logloss")
B = 1000  # reamostragens do bootstrap
rng = np.random.default_rng(42)


def modelos() -> dict:
    return {
        "Regressão logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "XGBoost": XGBClassifier(random_state=42, **PROD),
        "Random Forest": RandomForestClassifier(n_estimators=500, random_state=42, n_jobs=-1),
        "MLP": make_pipeline(StandardScaler(),
                             MLPClassifier(hidden_layer_sizes=(64, 32),
                                           max_iter=500, random_state=42)),
    }


def ic_diferenca(y, pa, pb) -> dict:
    """Bootstrap pareado de (A - B): AUC-ROC e acurácia."""
    n = len(y)
    d_auc, d_acc = [], []
    for _ in range(B):
        i = rng.integers(0, n, n)
        yi = y[i]
        if yi.min() == yi.max():
            continue
        d_auc.append(roc_auc_score(yi, pa[i]) - roc_auc_score(yi, pb[i]))
        d_acc.append(accuracy_score(yi, pa[i] >= .5) - accuracy_score(yi, pb[i] >= .5))
    f = lambda v: [round(float(x), 4) for x in
                   (np.mean(v), np.percentile(v, 2.5), np.percentile(v, 97.5))]
    return {"auc": f(d_auc), "acuracia": f(d_acc)}


def main() -> None:
    df = pd.read_csv("data/features_phases.csv")
    saida: dict = {}
    for corte in (10, 15, 20, 25):
        parte = df[df["cutoff_min"] == corte]
        X, y = parte[FEATURES], parte["blue_win"].to_numpy()
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        proba, res = {}, {}
        for nome, m in modelos().items():
            if corte != 15 and nome not in ("Regressão logística", "XGBoost"):
                continue
            p = cross_val_predict(m, X, y, cv=cv, method="predict_proba")[:, 1]
            proba[nome] = p
            res[nome] = {"acuracia": round(float(accuracy_score(y, p >= .5)), 4),
                         "auc": round(float(roc_auc_score(y, p)), 4)}
            print(f"{corte} min | {nome:20s} acc {res[nome]['acuracia']:.4f} "
                  f"auc {res[nome]['auc']:.4f}", flush=True)
        dif = {}
        for outro in proba:
            if outro == "XGBoost":
                continue
            dif[f"XGBoost - {outro}"] = ic_diferenca(y, proba["XGBoost"], proba[outro])
            print(f"   XGBoost - {outro}: {dif[f'XGBoost - {outro}']}", flush=True)
        saida[str(corte)] = {"n": int(len(y)), "modelos": res, "diferencas": dif}
    destino = Path("reports") / "baseline_e_diferencas.json"
    destino.write_text(json.dumps({
        "gerado_em": date.today().isoformat(), "base_linhas": int(len(df)),
        "cv": "estratificada, 5 dobras, seed 42", "bootstrap": f"{B} reamostragens pareadas, IC 95%",
        "diferencas_formato": "[media, limite inferior, limite superior]",
        "resultados": saida}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Artefato JSON: {destino}")


if __name__ == "__main__":
    main()
