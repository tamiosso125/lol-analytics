"""Experimentos 1 a 10 refeitos na base congelada (2026-11-04).

Os onze primeiros experimentos de enriquecimento (Quadro 5, Seção 5.4) foram
feitos antes do protocolo dos experimentos 12 a 19: bases de tamanhos
diferentes e sem intervalo de confiança. Aqui cada um dos que têm como ser
reproduzido é medido de novo no mesmo protocolo de `experiment_precisao.py`:
as 39.426 partidas de `data/features_phases.csv`, validação cruzada
estratificada de 5 dobras (semente 42), XGBoost de produção como referência e
*bootstrap* pareado do ganho de AUC-ROC (IC de 95%).

NÃO altera o modelo de produção nem os números do TCC.

Correspondência com o Quadro 5:
  1   Barão/Arauto            A01_barao_arauto
  2   Dispersão espacial      A02_dispersao
  3   Tuning por fase         tuning_aninhado (grade escolhida só no treino)
  4   Calibração              calibracao (isotônica e sigmoide)
  5,7 Ouro em itens           A05_ouro_itens
  6   Ofensivo × defensivo    A06_ofensivas, A06_defensivas
  8   Visão                   A08_visao_*
  9   Dragões por tipo        A09_dragoes_tipo
  10  Placas de torre         A10_placas
  11  Percentis (challenges)  NÃO REFEITO: o endpoint devolve o estado atual do
                              jogador e só existe para as partidas recentes da KR

Uso:  python -m src.models.experiment_antigos --cutoffs 15 25
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from xgboost import XGBClassifier

from src.models.experiment_precisao import BASE, MODELS, evaluate, paired_bootstrap

ARTEFATO = "reports/experimentos_antigos.json"
DRAG = [f"drag_{t}_diff" for t in ("fire", "water", "earth", "air", "hextech", "chemtech", "elder")]

SETS = {
    "base": BASE,
    "A01_barao_arauto": BASE + ["herald_diff", "baron_diff"],
    "A02_dispersao": BASE + ["spread_diff"],
    "A05_ouro_itens": BASE + ["item_gold_diff"],
    "A06_ofensivas": BASE + ["stat_attackDamage", "stat_abilityPower", "stat_attackSpeed"],
    "A06_defensivas": BASE + ["stat_armor", "stat_magicResist", "stat_healthMax"],
    "A08_visao_colocadas": BASE + ["ward_diff"],
    "A08_visao_destruidas": BASE + ["ward_kill_diff"],
    "A08_visao_ambas": BASE + ["ward_diff", "ward_kill_diff"],
    "A09_dragoes_tipo": BASE + DRAG,
    "A10_placas": BASE + ["plate_diff"],
}

GRADE = {"max_depth": [2, 3, 4], "learning_rate": [0.01, 0.03, 0.1], "n_estimators": [300, 600]}


def _vazio() -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = pd.Index([], name="match_id")
    return pd.DataFrame(index=idx), pd.DataFrame(index=idx)


def carregar() -> pd.DataFrame:
    v2 = pd.read_csv("data/features_v2.csv.gz")
    ant = pd.read_csv("data/features_antigos.csv.gz")
    df = v2.merge(ant, on=["match_id", "cutoff_min"], how="inner")
    assert len(df) == len(ant), "a base de features_antigos não bate com a de features_v2"
    return df


def tuning_aninhado(df: pd.DataFrame, cutoff: int) -> np.ndarray:
    """Probabilidades fora da dobra com a grade escolhida só no treino (3 dobras
    internas), para o ganho do tuning não ser otimista."""
    X, y = df[BASE].reset_index(drop=True), df["blue_win"].reset_index(drop=True)
    oof = np.full(len(X), np.nan)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=42).split(X, y):
        gs = GridSearchCV(
            XGBClassifier(random_state=42, eval_metric="logloss", n_jobs=4),
            GRADE, scoring="roc_auc", cv=StratifiedKFold(3, shuffle=True, random_state=1), n_jobs=1,
        )
        gs.fit(X.iloc[tr], y.iloc[tr])
        oof[te] = gs.predict_proba(X.iloc[te])[:, 1]
        print(f"    tuning dobra: {gs.best_params_}", flush=True)
    return oof


def calibracao(df: pd.DataFrame, cutoff: int) -> dict:
    """Calibração adicional por cima do XGBoost de produção, dentro da validação
    cruzada, e o desvio no estado de empate (a limitação da Seção 6.1)."""
    X, y = df[BASE].reset_index(drop=True), df["blue_win"].reset_index(drop=True)
    res = {}
    empate = (df["gold_diff"].abs() < 500).values
    obs = float(y[empate].mean())
    for nome, metodo in (("producao", None), ("sigmoide", "sigmoid"), ("isotonica", "isotonic")):
        oof = np.full(len(X), np.nan)
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=42).split(X, y):
            m = MODELS["xgb_prod"]()
            if metodo:
                m = CalibratedClassifierCV(m, method=metodo, cv=3)
            m.fit(X.iloc[tr], y.iloc[tr])
            oof[te] = m.predict_proba(X.iloc[te])[:, 1]
        m = MODELS["xgb_prod"]()
        if metodo:
            m = CalibratedClassifierCV(m, method=metodo, cv=3)
        m.fit(X, y)
        zero = float(m.predict_proba(pd.DataFrame([[0] * len(BASE)], columns=BASE))[0, 1])
        res[nome] = {"oof": oof, "auc": float(roc_auc_score(y, oof)), "p_estado_zero": zero}
    res["observado_empate"] = obs
    res["y"] = y.values
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoffs", nargs="+", type=int, default=[15, 25])
    ap.add_argument("--models", nargs="+", default=["xgb_prod", "logit"])
    ap.add_argument("--so", nargs="+", default=["sets", "tuning", "calibracao"])
    ap.add_argument("--bootstrap", type=int, default=300)
    args = ap.parse_args()

    df_all = carregar()
    champs, pl = _vazio()
    print(f"{df_all['match_id'].nunique()} partidas na base congelada")
    res = json.load(open(ARTEFATO, encoding="utf-8")) if os.path.exists(ARTEFATO) else {}

    def salvar():
        os.makedirs("reports", exist_ok=True)
        json.dump(res, open(ARTEFATO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    for cutoff in args.cutoffs:
        df = df_all[df_all["cutoff_min"] == cutoff].reset_index(drop=True)
        print(f"\n=== corte {cutoff} min, {len(df)} partidas ===", flush=True)
        r = res.setdefault(str(cutoff), {})
        refs = {}
        if "sets" in args.so:
            for setname, cols in SETS.items():
                for mname in args.models:
                    accs, aucs, oof, y = evaluate(df, champs, pl, cols, mname)
                    rec = {"acc": float(np.mean(accs)), "auc": float(np.mean(aucs)), "n_vars": len(cols)}
                    if setname == "base":
                        refs[mname] = (oof.copy(), y.copy())
                    else:
                        mean, lo, hi = paired_bootstrap(y, oof, refs[mname][0], b=args.bootstrap)
                        rec.update(delta_auc=mean, ic_lo=lo, ic_hi=hi)
                    r.setdefault(setname, {})[mname] = rec
                    d = f"  dAUC {rec['delta_auc']:+.4f} [{rec['ic_lo']:+.4f}, {rec['ic_hi']:+.4f}]" if "delta_auc" in rec else ""
                    print(f"{setname:<22}{mname:<9} acc {rec['acc']:.4f} auc {rec['auc']:.4f} ({len(cols)} var){d}", flush=True)
                    salvar()
        if "tuning" in args.so:
            if "xgb_prod" not in refs:
                _, _, oof_b, y = evaluate(df, champs, pl, BASE, "xgb_prod")
                refs["xgb_prod"] = (oof_b, y)
            oof = tuning_aninhado(df, cutoff)
            mean, lo, hi = paired_bootstrap(refs["xgb_prod"][1], oof, refs["xgb_prod"][0], b=args.bootstrap)
            r["tuning_aninhado"] = {"auc": float(roc_auc_score(refs["xgb_prod"][1], oof)),
                                    "delta_auc": mean, "ic_lo": lo, "ic_hi": hi, "grade": GRADE}
            print(f"tuning aninhado  auc {r['tuning_aninhado']['auc']:.4f}  dAUC {mean:+.4f} [{lo:+.4f}, {hi:+.4f}]", flush=True)
            salvar()
        if "calibracao" in args.so:
            c = calibracao(df, cutoff)
            ref = c["producao"]["oof"]
            out = {"observado_empate": c["observado_empate"]}
            for nome in ("producao", "sigmoide", "isotonica"):
                o = {"auc": c[nome]["auc"], "p_estado_zero": c[nome]["p_estado_zero"],
                     "desvio_empate_pp": 100 * (c[nome]["p_estado_zero"] - c["observado_empate"])}
                if nome != "producao":
                    mean, lo, hi = paired_bootstrap(c["y"], c[nome]["oof"], ref, b=args.bootstrap)
                    o.update(delta_auc=mean, ic_lo=lo, ic_hi=hi)
                out[nome] = o
                print(f"calibracao {nome:<10} auc {o['auc']:.4f}  P(estado zero) {o['p_estado_zero']:.3f}  "
                      f"desvio {o['desvio_empate_pp']:+.1f} pp" + (f"  dAUC {o['delta_auc']:+.4f}" if "delta_auc" in o else ""), flush=True)
            r["calibracao"] = out
            salvar()


if __name__ == "__main__":
    main()
