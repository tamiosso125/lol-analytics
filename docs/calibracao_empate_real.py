"""Calibração do XGBoost medida nas partidas empatadas REAIS, fora da dobra.

POR QUE ESTE SCRIPT EXISTE (2026-11-08, parecer do orientador): o Apêndice F
comparava a previsão para o estado sintético "tudo zero" (as cinco diferenças
iguais a zero, `taxa_base_por_corte.py`) com a taxa observada entre partidas
com diferença de ouro menor que 500. São populações diferentes: nas partidas
empatadas de verdade, XP, abates, torres e dragões quase nunca são todos zero.
A discrepância de 2,4 a 4,6 pp vinha dessa troca. Aqui a comparação é entre
grandezas do mesmo conjunto: a média da probabilidade prevista FORA DA DOBRA
nas partidas empatadas contra a taxa de vitória observada nessas mesmas
partidas. A previsão do estado zerado continua registrada só para explicar o
número antigo.

Também substitui as duas execuções que divergiam (Quadro 22 do Apêndice F com
calibrador de 5 dobras internas, `docs/experimento_calibracao.py`; Apêndice K,
experimento 4, com 3 dobras, `experiment_antigos.calibracao`) por um protocolo
só: 5 dobras externas estratificadas, semente 42; calibrador com 5 dobras
internas, ajustado só no treino de cada dobra externa.

Mede, sobre `data/features_phases.csv`:
  1. Por corte (10/15/20/25), XGBoost de produção: partidas empatadas, taxa
     observada (intervalo de Wilson), média prevista, diferença; calibração
     global por decis da probabilidade (maior desvio e desvio médio ponderado)
     e escore de Brier.
  2. Aos 15 e 25 min: produção, calibração sigmoidal e isotônica.
  3. A curva de calibração (decis) dos quatro cortes, em figura para o texto.

Uso:
    .venv\\Scripts\\python.exe docs\\calibracao_empate_real.py

Grava:
    reports/calibracao_empate_real.json
    reports/figuras_texto/fig_calibracao.png
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parent.parent
FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
PRODUCAO = dict(n_estimators=500, learning_rate=0.01, max_depth=3)
LIMITE_OURO = 500  # mesma definição de empate da Seção 5.3


def xgb() -> XGBClassifier:
    return XGBClassifier(eval_metric="logloss", random_state=42, n_jobs=4, **PRODUCAO)


def fora_da_dobra(X: pd.DataFrame, y: pd.Series, metodo: str | None) -> np.ndarray:
    """Probabilidade fora da dobra; o calibrador (se houver) só vê o treino da dobra."""
    oof = np.full(len(X), np.nan)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=42).split(X, y):
        m = xgb() if metodo is None else CalibratedClassifierCV(xgb(), method=metodo, cv=5)
        m.fit(X.iloc[tr], y.iloc[tr])
        oof[te] = m.predict_proba(X.iloc[te])[:, 1]
    return oof


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - m, c + m


def medir(d: pd.DataFrame, oof: np.ndarray) -> dict:
    y = d["blue_win"].to_numpy()
    emp = (d["gold_diff"].abs() < LIMITE_OURO).to_numpy()
    k, n = int(y[emp].sum()), int(emp.sum())
    lo, hi = wilson(k, n)
    decis = pd.DataFrame({"q": pd.qcut(oof, 10, labels=False), "p": oof, "y": y}).groupby("q").agg(
        prevista=("p", "mean"), observada=("y", "mean"), n=("y", "size"))
    desvio = (decis.prevista - decis.observada).abs()
    return {
        "partidas": int(len(d)), "auc": round(float(roc_auc_score(y, oof)), 4),
        "brier": round(float(brier_score_loss(y, oof)), 4),
        "empatadas": n, "taxa_observada": round(k / n, 4), "ic95_observada": [round(lo, 4), round(hi, 4)],
        "media_prevista_empatadas": round(float(oof[emp].mean()), 4),
        "diferenca_pp": round(100 * float(oof[emp].mean() - k / n), 2),
        "decis_maior_desvio_pp": round(100 * float(desvio.max()), 2),
        "decis_desvio_medio_pp": round(100 * float(np.average(desvio, weights=decis.n)), 2),
        "decis": [{"prevista": round(float(r.prevista), 4), "observada": round(float(r.observada), 4),
                   "n": int(r.n)} for r in decis.itertuples()],
    }


def figura(curvas: dict[int, list[dict]], destino: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.0, 5.0), dpi=200)
    ax.plot([0, 1], [0, 1], color="#9a9a9a", linestyle="--", linewidth=1, label="Calibração perfeita")
    estilos = {10: ("#1f4e79", "o"), 15: ("#c55a11", "s"), 20: ("#548235", "^"), 25: ("#7030a0", "D")}
    for corte, decis in curvas.items():
        cor, marca = estilos[corte]
        ax.plot([q["prevista"] for q in decis], [q["observada"] for q in decis], color=cor, marker=marca,
                markersize=4, linewidth=1.2, label=f"{corte} min")
    ax.set_xlabel("Probabilidade prevista de vitória do azul (média do decil)")
    ax.set_ylabel("Taxa observada de vitória do azul")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(RAIZ / "data" / "features_phases.csv")
    saida: dict = {"medido_em": date.today().isoformat(),
                   "protocolo": "StratifiedKFold(5, shuffle=True, random_state=42); calibrador "
                                "CalibratedClassifierCV(cv=5) só no treino de cada dobra; "
                                f"empate = |gold_diff| < {LIMITE_OURO}",
                   "producao_por_corte": {}, "variantes": {}}
    curvas = {}
    zero = pd.DataFrame([[0] * len(FEATURES)], columns=FEATURES)
    print(f"{'corte':>5} {'n':>6} {'emp':>5} {'obs':>7} {'prev':>7} {'dif':>6} {'zero':>7} "
          f"{'maxdec':>7} {'meddec':>7} {'auc':>7}")
    for corte in (10, 15, 20, 25):
        d = df[df.cutoff_min == corte].reset_index(drop=True)
        X, y = d[FEATURES], d["blue_win"]
        oof = fora_da_dobra(X, y, None)
        r = medir(d, oof)
        r["estado_zerado_modelo_completo"] = round(float(xgb().fit(X, y).predict_proba(zero)[0, 1]), 4)
        saida["producao_por_corte"][str(corte)] = r
        curvas[corte] = r["decis"]
        print(f"{corte:>5} {r['partidas']:>6} {r['empatadas']:>5} {r['taxa_observada']:>7.4f} "
              f"{r['media_prevista_empatadas']:>7.4f} {r['diferenca_pp']:>+6.2f} "
              f"{r['estado_zerado_modelo_completo']:>7.4f} {r['decis_maior_desvio_pp']:>7.2f} "
              f"{r['decis_desvio_medio_pp']:>7.2f} {r['auc']:>7.4f}", flush=True)
        if corte in (15, 25):
            saida["variantes"][str(corte)] = {"producao": {k: v for k, v in r.items() if k != "decis"}}
            for nome, metodo in (("sigmoide", "sigmoid"), ("isotonica", "isotonic")):
                rv = medir(d, fora_da_dobra(X, y, metodo))
                rv.pop("decis")
                saida["variantes"][str(corte)][nome] = rv
                print(f"      {corte} min {nome:<10} dif {rv['diferenca_pp']:+.2f} pp | maior decil "
                      f"{rv['decis_maior_desvio_pp']:.2f} | médio {rv['decis_desvio_medio_pp']:.2f} | "
                      f"auc {rv['auc']:.4f} | brier {rv['brier']:.4f}", flush=True)

    figura(curvas, RAIZ / "reports" / "figuras_texto" / "fig_calibracao.png")
    destino = RAIZ / "reports" / "calibracao_empate_real.json"
    destino.write_text(json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"gravado: {destino} e reports/figuras_texto/fig_calibracao.png")


if __name__ == "__main__":
    main()
