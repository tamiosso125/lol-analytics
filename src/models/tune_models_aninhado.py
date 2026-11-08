"""Busca em grade ANINHADA para XGBoost, Random Forest e MLP aos 15 minutos.

POR QUE ESTE SCRIPT EXISTE (2026-11-08, parecer do orientador): o Quadro 3
compara modelos ajustados por `tune_models_full`, que roda a grade nas 40.816
partidas e depois avalia a melhor combinação nas MESMAS dobras. A escolha dos
hiperparâmetros viu as partidas de teste, então o número pode ser otimista.
O parecer pede para dizer se a seleção ocorreu dentro das dobras de treino.
Aqui ela ocorre: em cada uma das 5 dobras externas (as mesmas do Quadro 3,
semente 42), a grade roda só no treino daquela dobra, com 3 dobras internas
(o mesmo desenho do experimento 3, `experiment_antigos.tuning_aninhado`), e a
combinação escolhida prevê a dobra de teste que a busca não viu.

Comparação: acurácia e AUC-ROC sobre as probabilidades agregadas fora da
dobra, como no Quadro 3, ao lado do valor não aninhado de
`reports/tune_models_39k.json`.

Uso:
    .venv\\Scripts\\python.exe -m src.models.tune_models_aninhado

Grava:
    reports/tune_models_aninhado.json
    reports/tune_models_aninhado.log
"""

from __future__ import annotations

import io
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.models.tune_models_full import GRADE_MLP, GRADE_RF, GRADE_XGB

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parents[2]
FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]


def modelos():
    return (
        ("XGBoost", lambda: XGBClassifier(eval_metric="logloss", random_state=42, n_jobs=1), GRADE_XGB),
        ("RandomForest", lambda: RandomForestClassifier(random_state=42), GRADE_RF),
        ("MLP", lambda: make_pipeline(StandardScaler(), MLPClassifier(max_iter=1000, random_state=42)), GRADE_MLP),
    )


def main() -> None:
    buf = io.StringIO()

    def emit(s: str = "") -> None:
        print(s, flush=True)
        buf.write(s + "\n")

    df = pd.read_csv(RAIZ / "data" / "features.csv")
    X, y = df[FEATURES].reset_index(drop=True), df["blue_win"].reset_index(drop=True)
    nao_aninhado = json.loads((RAIZ / "reports" / "tune_models_39k.json").read_text(encoding="utf-8"))
    externo = StratifiedKFold(5, shuffle=True, random_state=42)
    interno = StratifiedKFold(3, shuffle=True, random_state=1)

    emit(f"BUSCA EM GRADE ANINHADA — {len(df)} partidas, corte de 15 min, medido em {date.today()}")
    emit("externo: StratifiedKFold(5, shuffle, 42) | interno: StratifiedKFold(3, shuffle, 1) | roc_auc")
    saida = {"medido_em": date.today().isoformat(), "partidas": int(len(df)), "corte_min": 15,
             "externo": "StratifiedKFold(5, shuffle=True, random_state=42)",
             "interno": "StratifiedKFold(3, shuffle=True, random_state=1)", "modelos": {}}

    for nome, fabrica, grade in modelos():
        t0 = time.perf_counter()
        oof = np.full(len(X), np.nan)
        escolhas = []
        for i, (tr, te) in enumerate(externo.split(X, y), 1):
            gs = GridSearchCV(fabrica(), grade, scoring="roc_auc", cv=interno, n_jobs=-1)
            gs.fit(X.iloc[tr], y.iloc[tr])
            oof[te] = gs.predict_proba(X.iloc[te])[:, 1]
            escolhas.append({k: (list(v) if isinstance(v, tuple) else v) for k, v in gs.best_params_.items()})
            emit(f"  {nome} dobra {i}: {gs.best_params_}  ({time.perf_counter() - t0:.0f}s)")
        acc = float(accuracy_score(y, (oof >= 0.5).astype(int)))
        auc = float(roc_auc_score(y, oof))
        if nome == "XGBoost":
            ref = {"acuracia": nao_aninhado["XGBoost"]["acuracia_producao"],
                   "auc": nao_aninhado["XGBoost"]["auc_producao"],
                   "origem": "produção 500/0,01/3 (tune_models_39k.json)"}
        else:
            r = nao_aninhado[nome]
            ref = {"acuracia": r["acuracia_quadro3"], "auc": r["auc_quadro3"],
                   "origem": "grade nas 40.816, avaliada nas mesmas dobras (tune_models_39k.json)"}
        emit(f"{nome}: aninhado acurácia {acc:.4f} | AUC-ROC {auc:.4f}  "
             f"(não aninhado {ref['acuracia']:.4f} | {ref['auc']:.4f}; dif. AUC {auc - ref['auc']:+.4f})")
        saida["modelos"][nome] = {"acuracia": round(acc, 4), "auc": round(auc, 4),
                                  "escolhas_por_dobra": escolhas, "referencia_nao_aninhada": ref,
                                  "dif_auc": round(auc - ref["auc"], 4),
                                  "tempo_segundos": round(time.perf_counter() - t0, 1)}

    (RAIZ / "reports" / "tune_models_aninhado.json").write_text(
        json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
    (RAIZ / "reports" / "tune_models_aninhado.log").write_text(buf.getvalue(), encoding="utf-8")
    emit("gravado: reports/tune_models_aninhado.json e .log")


if __name__ == "__main__":
    main()
