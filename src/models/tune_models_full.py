"""Reexecuta o GridSearchCV na base final e ARQUIVA o log.

POR QUE ESTE SCRIPT EXISTE: a Seção 5.8 do TCC afirma que "um novo
GridSearchCV sobre as 39 mil linhas retornou os mesmos valores de
profundidade e um ajuste equivalente de árvores e taxa de aprendizado".
Essa afirmação não tinha artefato — nenhum log em `reports/` a sustentava.
É exatamente o padrão que produziu os outros quatro erros de número desta
rodada: uma conclusão escrita de memória. Aqui a medição é o que produz o
texto, e o log é o que a sustenta.

O que é medido, sobre `data/features.csv` (39.188 linhas do corte de 15 min):

  1. A grade completa do XGBoost (27 combinações × 5 folds), que é a que a
     afirmação da 5.8 cita.
  2. O desempenho dos hiperparâmetros DE PRODUÇÃO (500 / 0,01 / 3) dentro
     da mesma grade — para separar "a grade escolheu outra coisa" de "a
     grade escolheu outra coisa melhor".
  3. RandomForest e MLP, se `--completo`. O RF é o custo dominante (cada
     fit chega a dezenas de segundos com 500 árvores em 39 mil linhas) e
     NÃO é o que a 5.8 afirma, então fica atrás de flag.

Uso:
    .venv\\Scripts\\python.exe -m src.models.tune_models_full
    .venv\\Scripts\\python.exe -m src.models.tune_models_full --completo

Grava:
    reports/tune_models_39k.log   (texto, legivel)
    reports/tune_models_39k.json  (estruturado, para o TCC citar)
"""

from __future__ import annotations

import argparse
import io
import json
import platform
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
RAIZ = Path(__file__).resolve().parent.parent.parent

# Hiperparametros de PRODUCAO — os que `export_model.py` aplica. Sao a
# comparacao de referencia: a afirmacao da 5.8 e sobre eles Specifically.
PRODUCAO = {"n_estimators": 500, "learning_rate": 0.01, "max_depth": 3}

GRADE_XGB = {
    "n_estimators": [200, 300, 500],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [3, 4, 6],
}
GRADE_RF = {
    "n_estimators": [200, 300, 500],
    "max_depth": [None, 6, 10],
    "min_samples_leaf": [1, 2, 5],
}
GRADE_MLP = {
    "mlpclassifier__hidden_layer_sizes": [(32,), (64, 32), (128, 64)],
    "mlpclassifier__alpha": [0.0001, 0.001, 0.01],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--completo", action="store_true",
                    help="inclui RandomForest e MLP (lento)")
    args = ap.parse_args()

    df = pd.read_csv("data/features.csv")
    X, y = df[FEATURES], df["blue_win"]
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    buf = io.StringIO()

    def emit(*linhas: object) -> None:
        for ln in linhas:
            print(ln)
            buf.write(str(ln) + "\n")

    emit("=" * 74)
    emit("GRIDSEARCHCV NA BASE FINAL — tune_models_full")
    emit("=" * 74)
    emit(f"data          : {date.today().isoformat()}")
    emit(f"linhas        : {len(df)}")
    emit(f"taxa azul     : {y.mean():.4f}")
    emit(f"scikit-learn  : {sklearn.__version__}")
    emit(f"python        : {platform.python_version()}")
    emit(f"hyperpar. prod: {PRODUCAO}")
    emit(f"grade XGBoost : {GRADE_XGB}")
    emit(f"CV            : StratifiedKFold(5, shuffle=True, random_state=42)")
    emit(f"scoring       : roc_auc   |   n_jobs: todos os nucleos")
    emit("")

    resultados: dict[str, dict] = {}

    # ---- 1. grade completa do XGBoost -----------------------------------
    emit("-" * 74)
    emit("1. XGBoost — grade completa (27 combinacoes x 5 folds)")
    emit("-" * 74)
    t0 = time.perf_counter()
    busca = GridSearchCV(
        XGBClassifier(eval_metric="logloss", random_state=42),
        GRADE_XGB, scoring="roc_auc", cv=cv, n_jobs=-1,
    )
    busca.fit(X, y)
    dt = time.perf_counter() - t0

    melhor = busca.best_params_
    emit(f"melhor combinacao : {melhor}")
    emit(f"AUC da busca      : {busca.best_score_:.4f}")
    emit(f"tempo             : {dt:.1f}s")
    for r in sorted(
        zip(busca.cv_results_["params"],
            busca.cv_results_["mean_test_score"]),
        key=lambda x: -x[1],
    )[:5]:
        emit(f"  {r[0]}  AUC {r[1]:.4f}")

    # ---- 2. producao dentro da mesma grade -------------------------------
    emit("")
    emit("-" * 74)
    emit("2. Hiperparametros DE PRODUCAO, na mesma grade")
    emit("-" * 74)
    # O ranking de `busca` ja diz se producao estava no topo; recalcular o
    # AUC de producaocv deixa o numero explicito e independente do grid.
    producao_cv = cross_val_predict(
        XGBClassifier(eval_metric="logloss", random_state=42, **PRODUCAO),
        X, y, cv=cv, method="predict_proba",
    )[:, 1]
    pred = (producao_cv >= 0.5).astype(int)
    emit(f"{PRODUCAO}")
    emit(f"  acuracia : {accuracy_score(y, pred):.4f}")
    emit(f"  precisao : {precision_score(y, pred):.4f}")
    emit(f"  recall   : {recall_score(y, pred):.4f}")
    emit(f"  F1       : {f1_score(y, pred):.4f}")
    emit(f"  AUC-ROC  : {roc_auc_score(y, producao_cv):.4f}")
    delta_auc = busca.best_score_ - roc_auc_score(y, producao_cv)
    emit("")
    emit(f"AUC da melhor combinacao da grade : {busca.best_score_:.4f}")
    emit(f"AUC da combinacao de producao     : "
         f"{roc_auc_score(y, producao_cv):.4f}")
    emit(f"delta                             : {delta_auc:+.4f}")

    # ---- 3. a leitura que a 5.8 precisa ----------------------------------
    emit("")
    emit("-" * 74)
    emit("3. LEITURA PARA A SECAO 5.8")
    emit("-" * 74)
    prod_rank = None
    ordenado = sorted(
        zip(busca.cv_results_["params"], busca.cv_results_["mean_test_score"]),
        key=lambda x: -x[1],
    )
    for pos, (p, _s) in enumerate(ordenado, 1):
        if (p["n_estimators"] == PRODUCAO["n_estimators"]
                and p["learning_rate"] == PRODUCAO["learning_rate"]
                and p["max_depth"] == PRODUCAO["max_depth"]):
            prod_rank = pos
            break
    mesma_prof = melhor.get("max_depth") == PRODUCAO["max_depth"]
    emit(f"profundidade de producao : {PRODUCAO['max_depth']}")
    emit(f"profundidade vencedora  : {melhor.get('max_depth')}")
    emit(f"mesma profundidade?      : {mesma_prof}")
    emit(f"posicao de producao na grade: {prod_rank} de {len(ordenado)}")
    emit(f"delta de AUC             : {delta_auc:+.4f}")
    emit("")
    if abs(delta_auc) < 0.005:
        emit("VEREDITO: ajuste EQUIVALENTE (delta < 0,005). A 5.8 pode afirmar")
        emit("          que a grade não produz ganho relevante sobre os")
        emit("          parametros de produção — e portanto que a limitacao de")
        emit("          taxa-base NAO e subajuste.")
    else:
        emit(f"VEREDITO: a grade GANHA {delta_auc:+.4f} de AUC sobre producao. Isso")
        emit("          CONTRAI a afirmacao da 5.8 e precisa ser reescrito antes")
        emit("          de tratar a limitacao como nao-subajuste.")
    resultados["XGBoost"] = {
        "linhas": int(len(df)),
        "cv": "StratifiedKFold(5, shuffle=True, random_state=42)",
        "scoring": "roc_auc",
        "grade": GRADE_XGB,
        "producao": PRODUCAO,
        "melhor_combinacao": melhor,
        "auc_melhor": round(float(busca.best_score_), 4),
        "auc_producao": round(float(roc_auc_score(y, producao_cv)), 4),
        "delta_auc": round(float(delta_auc), 4),
        "posicao_producao_na_grade": prod_rank,
        "mesma_profundidade": bool(mesma_prof),
        "acuracia_producao": round(float(accuracy_score(y, pred)), 4),
        "tempo_segundos": round(dt, 1),
    }

    # ---- 4. opcionais ---------------------------------------------------
    if args.completo:
        for nome, est, grade in (
            ("RandomForest", RandomForestClassifier(random_state=42), GRADE_RF),
            ("MLP", make_pipeline(StandardScaler(),
                                  MLPClassifier(max_iter=1000, random_state=42)),
             GRADE_MLP),
        ):
            emit("")
            emit("-" * 74)
            emit(f"4. {nome} — grade completa")
            emit("-" * 74)
            t1 = time.perf_counter()
            b = GridSearchCV(est, grade, scoring="roc_auc", cv=cv, n_jobs=-1)
            b.fit(X, y)
            emit(f"melhor : {b.best_params_}")
            emit(f"AUC    : {b.best_score_:.4f}")
            emit(f"tempo  : {time.perf_counter() - t1:.1f}s")
            # best_score_ e a MEDIA do AUC por fold; o Quadro 3 calcula sobre as
            # probabilidades agregadas de cross_val_predict. Medir a melhor
            # combinacao do mesmo jeito do Quadro 3 deixa as duas comparaveis
            # (2026-11-02: a 5.4 dizia "apos ajuste" com RF/MLP na configuracao
            # de referencia; o texto passou a citar estes valores).
            proba = cross_val_predict(b.best_estimator_, X, y, cv=cv,
                                      method="predict_proba", n_jobs=-1)[:, 1]
            acc = accuracy_score(y, (proba >= 0.5).astype(int))
            auc = roc_auc_score(y, proba)
            emit(f"como no Quadro 3: acuracia {acc:.4f} | AUC-ROC {auc:.4f}")
            resultados[nome] = {
                "melhor_combinacao": b.best_params_,
                "auc_melhor": round(float(b.best_score_), 4),
                "acuracia_quadro3": round(float(acc), 4),
                "auc_quadro3": round(float(auc), 4),
            }

    relatorio = RAIZ / "reports"
    relatorio.mkdir(parents=True, exist_ok=True)
    (relatorio / "tune_models_39k.log").write_text(buf.getvalue(), encoding="utf-8")
    (relatorio / "tune_models_39k.json").write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    emit("")
    emit("gravado: reports/tune_models_39k.log")
    emit("gravado: reports/tune_models_39k.json")


if __name__ == "__main__":
    main()