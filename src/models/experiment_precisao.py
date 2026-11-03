"""Experimentos 12 a 18: dá para subir a acurácia/AUC sem violar o invariante 1?

Exploratório e sem meta de valor (decisão de 2026-11-03): explorar todas as
possibilidades para o trabalho ficar mais bem embasado. NÃO altera o modelo
de produção, o `data/features.csv` nem os números do TCC.

Base congelada: as partidas de `data/features_phases.csv` (as 39.426 do modelo
de produção), mesmo protocolo da Seção 5.4: validação cruzada estratificada de
5 dobras, semente 42, XGBoost com os parâmetros de produção como referência.

Conjuntos de variáveis (todos de `frames[: cutoff + 1]`, ver
`build_features_v2.py`; campeões e jogadores vêm de outras fontes, abaixo):
  base      as 5 diferenças de produção
  E12 traj  + ouro/XP/abates nos 3 e 5 min anteriores, ouro aos 5 e 10 min
  E13 func  + diferença por função (ouro, XP, nível, farm, dano) e atributos
  E14 obj   + arauto, barão, vastilarvas, inibidor, placas, 1º abate, 1ª torre
  E15 rico  = base + E12 + E13 + E14
  E16 camp  + taxa de vitória dos campeões (codificação FORA da dobra) e dos
              confrontos por rota. Só usa a escolha final de campeões, conhecida
              desde o início da partida.
  E17 jog   + taxa de vitória prévia dos jogadores e deles com o campeão, só
              com partidas ANTERIORES (game_creation estritamente menor).
              O elo atual de `players` é foto do futuro e NÃO é usado.
  E18 tudo  = E15 + E16 + E17

Uso:  python -m src.models.experiment_precisao --cutoffs 15 25
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

ARTEFATO = "reports/experimentos_precisao.json"
BASE = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
TRAJ = ["gold_d3", "gold_d5", "xp_d3", "xp_d5", "kill_d3", "kill_d5", "gold_5", "gold_10"]
LANE = [f"lane{i}_{k}" for i in range(1, 6) for k in ("gold", "xp", "lvl", "cs", "dmg")]
TEAM = ["level_diff", "cs_diff", "jungle_cs_diff", "dmg_diff", "gold_max_diff", "gold_min_diff"] + [
    f"stat_{s}" for s in ("attackDamage", "abilityPower", "armor", "magicResist", "healthMax", "attackSpeed")
]
OBJ = ["herald_diff", "baron_diff", "grub_diff", "inhib_diff", "plate_diff", "first_blood", "first_tower"]
CH = ["ch_te_diff", "ch_matchup_te"]
PL = ["pl_wr_diff", "pl_n_diff", "pl_cov_diff", "plch_wr_diff", "plch_n_diff"]
ROLES = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

SETS = {
    "base": BASE,
    "E12_trajetoria": BASE + TRAJ,
    "E13_funcao": BASE + LANE + TEAM,
    "E14_objetivos": BASE + OBJ,
    "E15_rico": BASE + TRAJ + LANE + TEAM + OBJ,
    "E16_campeoes": BASE + CH,
    "E17_jogadores": BASE + PL,
    "E18_tudo": BASE + TRAJ + LANE + TEAM + OBJ + CH + PL,
    "pre_jogo": CH + PL,
}

MODELS = {
    "xgb_prod": lambda: XGBClassifier(
        random_state=42, n_estimators=500, learning_rate=0.01, max_depth=3, eval_metric="logloss", n_jobs=4
    ),
    "xgb_rico": lambda: XGBClassifier(
        random_state=42, n_estimators=600, learning_rate=0.03, max_depth=4, subsample=0.8,
        colsample_bytree=0.8, min_child_weight=5, eval_metric="logloss", n_jobs=4,
    ),
    "logit": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)),
}


def load_context(match_ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Campeões por função (um linha por partida) e variáveis prévias de jogador."""
    from src.db import get_conn

    conn = get_conn()
    p = pd.read_sql(
        """SELECT p.match_id, p.puuid, p.team_id, p.team_position, p.champion_id, p.win,
                  m.game_creation
           FROM participants p JOIN matches m USING (match_id)
           WHERE p.match_id = ANY(%(ids)s)""",
        conn, params={"ids": match_ids},
    )
    conn.close()

    # campeões por função e lado
    wide = {}
    for side, tid in (("b", 100), ("r", 200)):
        s = p[(p.team_id == tid) & p.team_position.isin(ROLES)]
        s = s.drop_duplicates(["match_id", "team_position"])
        w = s.pivot(index="match_id", columns="team_position", values="champion_id")
        w.columns = [f"{side}_{c}" for c in w.columns]
        wide[side] = w
    champs = wide["b"].join(wide["r"], how="inner").dropna()

    # jogador: histórico só de partidas ANTERIORES (estritamente)
    p = p.sort_values(["puuid", "game_creation"]).reset_index(drop=True)
    p["win"] = p["win"].astype(int)
    g = p.groupby("puuid", sort=False)
    p["n_prior"] = g.cumcount()
    p["w_prior"] = g["win"].cumsum() - p["win"]
    # empate de game_creation do mesmo jogador não deveria existir; se existir, é conservador
    gc = p.groupby(["puuid", "champion_id"], sort=False)
    p["nc_prior"] = gc.cumcount()
    p["wc_prior"] = gc["win"].cumsum() - p["win"]
    p["wr"] = (p["w_prior"] + 10 * 0.5) / (p["n_prior"] + 10)
    p["wrc"] = (p["wc_prior"] + 5 * 0.5) / (p["nc_prior"] + 5)
    p["cov"] = (p["n_prior"] > 0).astype(int)
    agg = p.groupby(["match_id", "team_id"]).agg(
        wr=("wr", "mean"), n=("n_prior", "mean"), cov=("cov", "sum"), wrc=("wrc", "mean"), nc=("nc_prior", "mean")
    ).unstack("team_id")
    pl = pd.DataFrame(
        {
            "pl_wr_diff": agg[("wr", 100)] - agg[("wr", 200)],
            "pl_n_diff": agg[("n", 100)] - agg[("n", 200)],
            "pl_cov_diff": agg[("cov", 100)] - agg[("cov", 200)],
            "plch_wr_diff": agg[("wrc", 100)] - agg[("wrc", 200)],
            "plch_n_diff": agg[("nc", 100)] - agg[("nc", 200)],
        }
    ).fillna(0.0)
    return champs, pl


def _te_dict(champs: pd.DataFrame, y: pd.Series, m: int = 30) -> tuple[dict, dict]:
    """Taxas de vitória suavizadas por campeão e por confronto de rota (lado azul)."""
    single = {}
    rows = []
    for role in ROLES:
        rows.append(pd.DataFrame({"c": champs[f"b_{role}"].values, "w": y.values}))
        rows.append(pd.DataFrame({"c": champs[f"r_{role}"].values, "w": 1 - y.values}))
    long = pd.concat(rows)
    s = long.groupby("c")["w"].agg(["sum", "count"])
    single = ((s["sum"] + m * 0.5) / (s["count"] + m)).to_dict()
    pair = {}
    for role in ROLES:
        d = pd.DataFrame({"b": champs[f"b_{role}"].values, "r": champs[f"r_{role}"].values, "w": y.values})
        s = d.groupby(["b", "r"])["w"].agg(["sum", "count"])
        for (b, r), row in s.iterrows():
            pair[(role, b, r)] = (row["sum"] + m * 0.5) / (row["count"] + m)
    return single, pair


def _te_apply(champs: pd.DataFrame, single: dict, pair: dict) -> pd.DataFrame:
    b = np.mean([champs[f"b_{r}"].map(single).fillna(0.5).values for r in ROLES], axis=0)
    r_ = np.mean([champs[f"r_{r}"].map(single).fillna(0.5).values for r in ROLES], axis=0)
    mu = np.zeros(len(champs))
    for role in ROLES:
        mu += np.array([pair.get((role, x, y), 0.5) - 0.5 for x, y in zip(champs[f"b_{role}"], champs[f"r_{role}"])])
    return pd.DataFrame({"ch_te_diff": b - r_, "ch_matchup_te": mu}, index=champs.index)


def champ_features(champs_tr: pd.DataFrame, y_tr: pd.Series, champs_te: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Treino: codificação fora da dobra interna (sem ver o próprio rótulo).
    Teste: dicionário do treino inteiro."""
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    tr_feat = pd.DataFrame(index=champs_tr.index, columns=CH, dtype=float)
    for a, b in inner.split(champs_tr, y_tr):
        s, p = _te_dict(champs_tr.iloc[a], y_tr.iloc[a])
        tr_feat.iloc[b] = _te_apply(champs_tr.iloc[b], s, p).values
    s, p = _te_dict(champs_tr, y_tr)
    return tr_feat, _te_apply(champs_te, s, p)


def evaluate(df: pd.DataFrame, champs: pd.DataFrame, pl: pd.DataFrame, cols: list[str], model_name: str):
    """Retorna (métricas por dobra, previsões fora da dobra alinhadas a df)."""
    y = df["blue_win"].reset_index(drop=True)
    X = df.reset_index(drop=True)
    ch = champs.reindex(X["match_id"]).reset_index(drop=True)
    plf = pl.reindex(X["match_id"]).reset_index(drop=True).fillna(0.0)
    X = pd.concat([X, plf], axis=1)
    use_ch = any(c in CH for c in cols)
    have = ch.notna().all(axis=1).values if use_ch else np.ones(len(X), bool)
    oof = np.full(len(X), np.nan)
    accs, aucs = [], []
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for tr, te in cv.split(X, y):
        Xtr, Xte = X.iloc[tr][[c for c in cols if c not in CH]].copy(), X.iloc[te][[c for c in cols if c not in CH]].copy()
        if use_ch:
            tr_ok, te_ok = tr[have[tr]], te[have[te]]
            ftr, fte = champ_features(ch.iloc[tr_ok], y.iloc[tr_ok], ch.iloc[te_ok])
            Xtr = pd.concat([Xtr.loc[tr_ok], ftr.set_index(Xtr.loc[tr_ok].index)], axis=1)[cols]
            Xte = pd.concat([Xte.loc[te_ok], fte.set_index(Xte.loc[te_ok].index)], axis=1)[cols]
            ytr, te_idx = y.iloc[tr_ok], te_ok
        else:
            Xtr, Xte = Xtr[cols], Xte[cols]
            ytr, te_idx = y.iloc[tr], te
        mdl = MODELS[model_name]()
        mdl.fit(Xtr, ytr)
        pr = mdl.predict_proba(Xte)[:, 1]
        oof[te_idx] = pr
        yt = y.iloc[te_idx]
        accs.append(accuracy_score(yt, pr >= 0.5))
        aucs.append(roc_auc_score(yt, pr))
    return accs, aucs, oof, y.values


def paired_bootstrap(y, p_new, p_old, b=300, seed=42):
    m = ~(np.isnan(p_new) | np.isnan(p_old))
    y, p_new, p_old = y[m], p_new[m], p_old[m]
    rng = np.random.default_rng(seed)
    d = []
    n = len(y)
    for _ in range(b):
        i = rng.integers(0, n, n)
        if y[i].min() == y[i].max():
            continue
        d.append(roc_auc_score(y[i], p_new[i]) - roc_auc_score(y[i], p_old[i]))
    d = np.array(d)
    return float(d.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoffs", nargs="+", type=int, default=[15, 25])
    ap.add_argument("--models", nargs="+", default=["xgb_prod", "xgb_rico", "logit"])
    ap.add_argument("--sets", nargs="+", default=list(SETS))
    ap.add_argument("--bootstrap", type=int, default=300)
    args = ap.parse_args()

    feats = pd.read_csv("data/features_v2.csv.gz")
    ids = feats["match_id"].unique().tolist()
    print(f"{len(ids)} partidas na base congelada; carregando campeões e histórico de jogadores")
    champs, pl = load_context(ids)
    print(f"campeões completos em {len(champs)} partidas; histórico prévio com cobertura média "
          f"{(pl['pl_cov_diff'].abs() > 0).mean():.2%} das partidas")

    res = json.load(open(ARTEFATO, encoding="utf-8")) if os.path.exists(ARTEFATO) else {}
    for cutoff in args.cutoffs:
        df = feats[feats["cutoff_min"] == cutoff].reset_index(drop=True)
        print(f"\n=== corte {cutoff} min, {len(df)} partidas ===")
        ref = None
        for setname in args.sets:
            for mname in args.models:
                if mname == "logit" and setname not in ("base", "E15_rico", "E18_tudo"):
                    continue
                accs, aucs, oof, y = evaluate(df, champs, pl, SETS[setname], mname)
                if setname == "base" and mname == "xgb_prod":
                    ref = (oof.copy(), y.copy())
                rec = {"acc": float(np.mean(accs)), "auc": float(np.mean(aucs)), "n_vars": len(SETS[setname]),
                       "n": int((~np.isnan(oof)).sum())}
                if ref is not None and not (setname == "base" and mname == "xgb_prod"):
                    mean, lo, hi = paired_bootstrap(y, oof, ref[0], b=args.bootstrap)
                    rec.update(delta_auc=mean, ic_lo=lo, ic_hi=hi)
                res.setdefault(str(cutoff), {}).setdefault(setname, {})[mname] = rec
                d = f"  dAUC {rec['delta_auc']:+.4f} [{rec['ic_lo']:+.4f}, {rec['ic_hi']:+.4f}]" if "delta_auc" in rec else ""
                print(f"{setname:<16}{mname:<10} acc {rec['acc']:.4f}  auc {rec['auc']:.4f}  ({rec['n_vars']} var){d}", flush=True)
                os.makedirs("reports", exist_ok=True)
                json.dump(res, open(ARTEFATO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
