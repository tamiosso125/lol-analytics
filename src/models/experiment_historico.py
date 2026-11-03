"""Experimento 19: o histórico prévio do jogador ajuda quando há histórico de verdade?

No experimento 17 só 31% das partidas tinham algum histórico (a base só guarda
as partidas coletadas, e a maioria dos 38.898 jogadores aparece uma ou duas
vezes). O ganho médio foi pequeno, mas isso pode ser diluição: quase metade das
partidas tem jogadores sem histórico. Este script mede o efeito POR ESTRATO de
cobertura, para responder se mais cobertura valeria o esforço de coletar.

Histórico = só partidas do mesmo jogador com `game_creation` ESTRITAMENTE
anterior (invariante 1). O elo atual de `players` não é usado (foto do futuro).
Variáveis por jogador: taxa de vitória suavizada (toda a história e as últimas
5), nº de jogos, taxa com o campeão. Por partida: média por time, diferença
azul menos vermelho.

Estratos (nº de jogadores da partida com >= 3 partidas prévias): 0, 1-2, 3-4,
5 ou mais. Em cada um: estado rico (E15) contra E15 + histórico, mesmo
protocolo (5 dobras, semente 42), IC do ganho por bootstrap pareado.

Uso:  python -m src.models.experiment_historico --cutoffs 15 25
Gera: reports/experimento_historico.json
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from src.models.experiment_precisao import BASE, LANE, MODELS, OBJ, TEAM, TRAJ

E15 = BASE + TRAJ + LANE + TEAM + OBJ
HIST = ["h_wr_diff", "h_wr5_diff", "h_n_diff", "h_wrc_diff", "h_cov"]


def historico(match_ids: list[str]) -> pd.DataFrame:
    from src.db import get_conn

    conn = get_conn()
    p = pd.read_sql(
        """SELECT p.match_id, p.puuid, p.team_id, p.champion_id, p.win, m.game_creation
           FROM participants p JOIN matches m USING (match_id)""",
        conn,
    )
    conn.close()
    p["win"] = p["win"].astype(int)
    p = p.sort_values(["puuid", "game_creation", "match_id"]).reset_index(drop=True)
    g = p.groupby("puuid", sort=False)
    p["n"] = g.cumcount()
    p["w"] = g["win"].cumsum() - p["win"]
    p["wr"] = (p["w"] + 5.0) / (p["n"] + 10.0)
    # últimas 5 PARTIDAS ANTERIORES: soma móvel deslocada em 1 (exclui a atual)
    shifted = g["win"].shift(1)
    p["w5"] = shifted.groupby(p["puuid"]).rolling(5, min_periods=1).sum().reset_index(level=0, drop=True)
    p["n5"] = shifted.groupby(p["puuid"]).rolling(5, min_periods=1).count().reset_index(level=0, drop=True)
    p["wr5"] = (p["w5"].fillna(0) + 2.5) / (p["n5"].fillna(0) + 5.0)
    gc = p.groupby(["puuid", "champion_id"], sort=False)
    p["nc"] = gc.cumcount()
    p["wc"] = gc["win"].cumsum() - p["win"]
    p["wrc"] = (p["wc"] + 2.5) / (p["nc"] + 5.0)
    p["tem3"] = (p["n"] >= 3).astype(int)
    p = p[p["match_id"].isin(set(match_ids))]
    a = p.groupby(["match_id", "team_id"]).agg(wr=("wr", "mean"), wr5=("wr5", "mean"), n=("n", "mean"),
                                               wrc=("wrc", "mean"), t3=("tem3", "sum")).unstack("team_id")
    out = pd.DataFrame({
        "h_wr_diff": a[("wr", 100)] - a[("wr", 200)], "h_wr5_diff": a[("wr5", 100)] - a[("wr5", 200)],
        "h_n_diff": a[("n", 100)] - a[("n", 200)], "h_wrc_diff": a[("wrc", 100)] - a[("wrc", 200)],
        "h_cov": a[("t3", 100)] + a[("t3", 200)],
    }).fillna(0.0)
    return out


def cv_oof(X: pd.DataFrame, y: np.ndarray, mname: str) -> np.ndarray:
    oof = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=42).split(X, y):
        m = MODELS[mname]()
        m.fit(X.iloc[tr], y[tr])
        oof[te] = m.predict_proba(X.iloc[te])[:, 1]
    return oof


def boot(y, a, b, B=400, seed=42):
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(B):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        d.append(roc_auc_score(y[i], a[i]) - roc_auc_score(y[i], b[i]))
    return [round(float(np.percentile(d, q)), 4) for q in (50, 2.5, 97.5)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoffs", nargs="+", type=int, default=[15, 25])
    args = ap.parse_args()
    feats = pd.read_csv("data/features_v2.csv.gz")
    h = historico(feats["match_id"].unique().tolist())
    feats = feats.merge(h, left_on="match_id", right_index=True, how="left")
    feats[HIST] = feats[HIST].fillna(0.0)

    res = {}
    for corte in args.cutoffs:
        df = feats[feats["cutoff_min"] == corte].reset_index(drop=True)
        cov = df["h_cov"]
        print(f"\n=== corte {corte} min ===  cobertura (jogadores com >=3 partidas prévias): "
              f"média {cov.mean():.2f}; distribuição {cov.clip(upper=5).value_counts().sort_index().to_dict()}")
        strata = {"0": cov == 0, "1-2": cov.between(1, 2), "3-4": cov.between(3, 4), "5+": cov >= 5, "todas": cov >= 0}
        res[str(corte)] = {}
        for nome, mask in strata.items():
            d = df[mask].reset_index(drop=True)
            if len(d) < 800:
                print(f"{nome:>5}: n={len(d)} (pequeno, pulado)")
                continue
            y = d["blue_win"].to_numpy()
            for mname in ("logit", "xgb_prod"):
                a = cv_oof(d[E15], y, mname)
                b = cv_oof(d[E15 + HIST], y, mname)
                rec = {"n": int(len(d)), "auc_sem": round(float(roc_auc_score(y, a)), 4),
                       "auc_com": round(float(roc_auc_score(y, b)), 4), "dauc_ic": boot(y, b, a)}
                res[str(corte)].setdefault(nome, {})[mname] = rec
                print(f"{nome:>5} n={rec['n']:5d} {mname:8s} AUC sem {rec['auc_sem']:.4f} com {rec['auc_com']:.4f} "
                      f"ganho {rec['dauc_ic'][0]:+.4f} [{rec['dauc_ic'][1]:+.4f}, {rec['dauc_ic'][2]:+.4f}]", flush=True)
    with open("reports/experimento_historico.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
