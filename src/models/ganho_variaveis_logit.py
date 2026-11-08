"""Ganho das variáveis novas medido DENTRO do mesmo classificador.

POR QUE ESTE SCRIPT EXISTE (2026-11-08, parecer do orientador): o "+0,0078"
dos experimentos 12 a 19 compara a regressão logística com 64 variáveis (E18)
contra o XGBoost de produção com 5. A diferença mistura duas coisas: as
variáveis novas e a troca de classificador. Para isolar as variáveis, aqui a
referência é a própria regressão logística com as 5 variáveis de produção, e o
XGBoost de produção é comparado consigo mesmo.

Mesmo protocolo de `experiment_precisao` (de onde vêm `evaluate`, os
conjuntos e o bootstrap pareado por partida): 5 dobras estratificadas,
semente 42, intervalo de 95% por 300 reamostragens das partidas.

Uso:
    .venv\\Scripts\\python.exe -m src.models.ganho_variaveis_logit

Grava:
    reports/ganho_variaveis_logit.json
"""
import json
import sys
from datetime import date

import pandas as pd
from sklearn.metrics import roc_auc_score

from src.models.experiment_precisao import SETS, evaluate, load_context, paired_bootstrap

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ARTEFATO = "reports/ganho_variaveis_logit.json"


def main() -> None:
    feats = pd.read_csv("data/features_v2.csv.gz")
    champs, pl = load_context(feats["match_id"].unique().tolist())
    res = {"medido_em": date.today().isoformat(),
           "protocolo": "StratifiedKFold(5, shuffle, 42); bootstrap pareado por partida, 300 reamostragens",
           "cortes": {}}
    for cutoff in (15, 25):
        df = feats[feats["cutoff_min"] == cutoff].reset_index(drop=True)
        print(f"=== corte {cutoff} min, {len(df)} partidas ===", flush=True)
        saida = {}
        for modelo in ("logit", "xgb_prod"):
            _, _, oof_base, y = evaluate(df, champs, pl, SETS["base"], modelo)
            saida[modelo] = {"base_auc": round(float(roc_auc_score(y, oof_base)), 4)}
            for conjunto in ("E15_rico", "E18_tudo"):
                _, _, oof, _ = evaluate(df, champs, pl, SETS[conjunto], modelo)
                ok = ~pd.isna(oof)
                media, lo, hi = paired_bootstrap(y, oof, oof_base)
                saida[modelo][conjunto] = {
                    "n_vars": len(SETS[conjunto]), "n": int(ok.sum()),
                    "auc": round(float(roc_auc_score(y[ok], oof[ok])), 4),
                    "ganho_auc": round(media, 4), "ic_lo": round(lo, 4), "ic_hi": round(hi, 4)}
                print(f"  {modelo:<9}{conjunto:<10} ganho {media:+.4f} [{lo:+.4f}, {hi:+.4f}]", flush=True)
        res["cortes"][str(cutoff)] = saida
    with open(ARTEFATO, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"gravado: {ARTEFATO}")


if __name__ == "__main__":
    main()
