"""Os ganhos dos experimentos 12 a 18 sobrevivem a treinar no passado e testar no futuro?

Exploratório; NÃO altera o modelo de produção nem o TCC. Mesmas três divisões
de `holdout_temporal.py` (cronológica 80/20, por *patch* 16.10-16.13 contra
16.14-16.19, aleatória de mesmo tamanho), mas comparando conjuntos de variáveis
de `experiment_precisao.py`: base (5 variáveis), E15 (estado rico) e E18
(estado rico + campeões + histórico prévio do jogador).

Cuidados contra vazamento:
  - a codificação dos campeões é ajustada só no treino (com dobra interna
    para as linhas do próprio treino, ver `champ_features`);
  - o histórico do jogador usa só partidas com `game_creation` anterior, então
    uma partida de teste nunca vê o resultado de partida posterior.

Uso:  python -m src.models.holdout_precisao --cutoffs 15 25
Gera: reports/holdout_precisao.json
"""
import argparse
import json
from datetime import date

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from src.models.experiment_precisao import CH, MODELS, SETS, champ_features, load_context

PATCHES_TREINO = ("16.10", "16.11", "16.12", "16.13")
CONJUNTOS = ["base", "E13_funcao", "E15_rico", "E16_campeoes", "E18_tudo"]
MODELOS = ["xgb_prod", "logit"]
B = 500


def meta(match_ids: list[str]) -> pd.DataFrame:
    from src.db import get_conn

    conn = get_conn()
    m = pd.read_sql(
        "SELECT match_id, game_creation AS quando, "
        "split_part(game_version,'.',1) || '.' || split_part(game_version,'.',2) AS patch "
        "FROM matches WHERE match_id = ANY(%(ids)s)",
        conn, params={"ids": match_ids},
    )
    conn.close()
    return m


def ajustar_prever(tr: pd.DataFrame, te: pd.DataFrame, champs: pd.DataFrame, cols: list[str], mname: str):
    tr, te = tr.copy(), te.copy()
    if any(c in CH for c in cols):
        tr = tr[tr["match_id"].isin(champs.index)]
        te = te[te["match_id"].isin(champs.index)]
        c_tr, c_te = champs.loc[tr["match_id"]], champs.loc[te["match_id"]]
        ftr, fte = champ_features(c_tr, pd.Series(tr["blue_win"].values, index=c_tr.index), c_te)
        tr[CH] = ftr.values
        te[CH] = fte.values
    mdl = MODELS[mname]()
    mdl.fit(tr[cols], tr["blue_win"])
    p = mdl.predict_proba(te[cols])[:, 1]
    return te, p


def ic_diff(y, p_new, p_ref, seed=42):
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(B):
        i = rng.integers(0, len(y), len(y))
        if y[i].min() == y[i].max():
            continue
        d.append(roc_auc_score(y[i], p_new[i]) - roc_auc_score(y[i], p_ref[i]))
    d = np.array(d)
    return [round(float(np.percentile(d, q)), 4) for q in (50, 2.5, 97.5)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoffs", nargs="+", type=int, default=[15, 25])
    args = ap.parse_args()

    feats = pd.read_csv("data/features_v2.csv.gz")
    ids = feats["match_id"].unique().tolist()
    champs, pl = load_context(ids)
    feats = feats.merge(meta(ids), on="match_id", how="inner").merge(pl, left_on="match_id", right_index=True, how="left")
    feats[list(pl.columns)] = feats[list(pl.columns)].fillna(0.0)
    feats["regiao"] = feats["match_id"].str.split("_").str[0]

    saida = {"gerado_em": date.today().isoformat(), "patches_treino": list(PATCHES_TREINO), "cortes": {}}
    for corte in args.cutoffs:
        parte = feats[feats["cutoff_min"] == corte].sort_values("quando").reset_index(drop=True)
        k = int(len(parte) * 0.8)
        cron_tr, cron_te = parte.iloc[:k], parte.iloc[k:]
        pat_tr = parte[parte["patch"].isin(PATCHES_TREINO)]
        pat_te = parte[~parte["patch"].isin(PATCHES_TREINO)]
        al_tr, al_te = train_test_split(parte, test_size=len(cron_te), stratify=parte["blue_win"], random_state=42)
        divs = {"cronologica": (cron_tr, cron_te), "por_patch": (pat_tr, pat_te), "aleatoria": (al_tr, al_te)}
        saida["cortes"][str(corte)] = {}
        for dname, (tr, te) in divs.items():
            ref_p = ref_y = None
            for cset in CONJUNTOS:
                for mname in MODELOS:
                    if mname == "logit" and cset not in ("base", "E15_rico", "E18_tudo"):
                        continue
                    te_ok, p = ajustar_prever(tr, te, champs, SETS[cset], mname)
                    y = te_ok["blue_win"].to_numpy()
                    rec = {"n_treino": int(len(tr)), "n_teste": int(len(te_ok)),
                           "acc": round(float(accuracy_score(y, p >= 0.5)), 4),
                           "auc": round(float(roc_auc_score(y, p)), 4)}
                    ids = te_ok["match_id"].to_numpy()
                    if cset == "base" and mname == "xgb_prod":
                        ref_p, ref_y, ref_ids = p.copy(), y.copy(), ids.copy()
                    elif ref_p is not None:
                        # pareia pelas partidas em comum (campeões ausentes tiram 1 ou 2 do teste)
                        comum, a, b = np.intersect1d(ids, ref_ids, return_indices=True)
                        rec["dauc_vs_base_xgb"] = ic_diff(y[a], p[a], ref_p[b])
                    saida["cortes"][str(corte)].setdefault(dname, {}).setdefault(cset, {})[mname] = rec
                    d = f" dAUC {rec['dauc_vs_base_xgb'][0]:+.4f} {rec['dauc_vs_base_xgb'][1:]}" if "dauc_vs_base_xgb" in rec else ""
                    print(f"{corte} min | {dname:11s} | {cset:13s} | {mname:8s} | n {rec['n_treino']}/{rec['n_teste']} "
                          f"| acc {rec['acc']:.4f} auc {rec['auc']:.4f}{d}", flush=True)
    with open("reports/holdout_precisao.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print("Artefato: reports/holdout_precisao.json")


if __name__ == "__main__":
    main()
