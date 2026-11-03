"""Treino no passado, teste no futuro: a validação cruzada aleatória esconde algo?

Por que este script existe: o TCC usa validação cruzada estratificada ALEATÓRIA
(Seção 4.4). Kaufman et al. (2012, seções 3.3 e 3.4) avisam que, quando os
dados mudam com o tempo (aqui, os *patches* do jogo) e os exemplos não são
independentes (os mesmos jogadores jogam várias partidas), treinar com partidas
misturadas no tempo pode inflar o resultado. A pergunta é: se o modelo for
treinado só com partidas ANTERIORES e testado em partidas POSTERIORES, a
acurácia e a AUC-ROC caem?

Três divisões, todas com o MESMO modelo e as mesmas cinco variáveis:

  1. cronológica 80/20: as 80% partidas mais antigas treinam, as 20% mais
     recentes testam;
  2. por *patch*: treina nos *patches* 16.10 a 16.13 e testa nos 16.14 a 16.19
     (o teste só vê regras de jogo que o treino nunca viu);
  3. aleatória estratificada com o mesmo tamanho de teste da divisão 1 (a
     referência: é o que a validação cruzada do TCC mede).

A diferença entre (1) ou (2) e (3) é o quanto a mistura no tempo inflava o
resultado. IC de 95% da AUC por *bootstrap* (1.000 reamostragens, semente 42).

Cuidado com a leitura: o tempo pode se confundir com a região, porque a coleta
não foi simultânea; por isso o script imprime a composição por região de cada
lado. Não se compara com a validação cruzada de 5 dobras do Quadro 3, e sim
com a divisão aleatória de mesmo tamanho (3), para isolar o efeito do tempo.

Uso:  python -m src.models.holdout_temporal
Gera: imprime os quadros e grava reports/holdout_temporal.json.
"""
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.db import get_conn

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
PROD = dict(n_estimators=500, learning_rate=0.01, max_depth=3, eval_metric="logloss")
B = 1000
PATCHES_TREINO = ("16.10", "16.11", "16.12", "16.13")
rng = np.random.default_rng(42)


def modelos() -> dict:
    return {
        "XGBoost": XGBClassifier(random_state=42, **PROD),
        "Regressão logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    }


def carregar() -> pd.DataFrame:
    """Variáveis por corte, com data da partida e *patch* vindos do banco."""
    df = pd.read_csv("data/features_phases.csv")
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "SELECT match_id, game_creation, "
            "split_part(game_version,'.',1) || '.' || split_part(game_version,'.',2) "
            "FROM matches"
        )
        meta = pd.DataFrame(cur.fetchall(), columns=["match_id", "quando", "patch"])
    df = df.merge(meta, on="match_id", how="inner")
    df["quando"] = pd.to_datetime(df["quando"], utc=True)
    df["regiao"] = df["match_id"].str.split("_").str[0]
    return df


def auc_ic(y, p) -> list:
    aucs = []
    for _ in range(B):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        aucs.append(roc_auc_score(y[i], p[i]))
    return [round(float(np.percentile(aucs, q)), 4) for q in (2.5, 97.5)]


def medir(modelo, tr: pd.DataFrame, te: pd.DataFrame) -> dict:
    modelo.fit(tr[FEATURES], tr["blue_win"])
    p = modelo.predict_proba(te[FEATURES])[:, 1]
    y = te["blue_win"].to_numpy()
    return {
        "n_treino": int(len(tr)), "n_teste": int(len(te)),
        "acuracia": round(float(accuracy_score(y, p >= 0.5)), 4),
        "auc": round(float(roc_auc_score(y, p)), 4),
        "auc_ic95": auc_ic(y, p),
    }


def divisoes(parte: pd.DataFrame) -> dict:
    """As três divisões para um corte de tempo."""
    parte = parte.sort_values("quando")
    k = int(len(parte) * 0.8)
    cron_tr, cron_te = parte.iloc[:k], parte.iloc[k:]
    pat_tr = parte[parte["patch"].isin(PATCHES_TREINO)]
    pat_te = parte[~parte["patch"].isin(PATCHES_TREINO)]
    alea_tr, alea_te = train_test_split(
        parte, test_size=len(cron_te), stratify=parte["blue_win"], random_state=42)
    return {"cronologica": (cron_tr, cron_te), "por_patch": (pat_tr, pat_te),
            "aleatoria": (alea_tr, alea_te)}


def main() -> None:
    df = carregar()
    saida: dict = {"gerado_em": date.today().isoformat(), "partidas": int(df["match_id"].nunique()),
                   "patches_treino_por_patch": list(PATCHES_TREINO), "cortes": {}}
    for corte in (10, 15, 20, 25):
        parte = df[df["cutoff_min"] == corte]
        saida["cortes"][str(corte)] = {}
        for nome_div, (tr, te) in divisoes(parte).items():
            reg_tr = tr["regiao"].value_counts(normalize=True).round(3).to_dict()
            reg_te = te["regiao"].value_counts(normalize=True).round(3).to_dict()
            for nome, m in modelos().items():
                r = medir(m, tr, te)
                r["regioes_treino"], r["regioes_teste"] = reg_tr, reg_te
                r["azul_teste"] = round(float(te["blue_win"].mean()), 4)
                saida["cortes"][str(corte)].setdefault(nome_div, {})[nome] = r
                print(f"{corte:2d} min | {nome_div:11s} | {nome:19s} | n {r['n_treino']:5d}/{r['n_teste']:5d} "
                      f"| acc {r['acuracia']:.4f} | auc {r['auc']:.4f} {r['auc_ic95']}", flush=True)
    destino = Path("reports") / "holdout_temporal.json"
    destino.write_text(json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Artefato JSON: {destino}")


if __name__ == "__main__":
    main()
