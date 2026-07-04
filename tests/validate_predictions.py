"""Bateria de validação comportamental do modelo de predição (produção).

Não substitui as métricas de held-out test já reportadas (train_baseline.py
/ tune_models.py) — testa outra coisa: se o modelo exportado (usado pelo
/predict e pela análise de partida) se comporta como um analista esperaria,
em cenários que não estão necessariamente no dataset de teste:

  1. Monotonicidade: mais ouro/XP/abates/torres/dragões para o azul nunca
     deveria DIMINUIR a probabilidade de vitória do azul.
  2. Casos extremos: uma vantagem enorme em tudo deve dar probabilidade
     muito alta (não 100% cravado — o modelo não deveria ser overconfident
     além do que os dados sustentam — mas claramente decisivo).
  3. Taxa-base por fase: com tudo empatado, a probabilidade deve refletir o
     viés de lado já documentado (< 50%, favorecendo o vermelho).
  4. Consistência entre fases (achado do SHAP): a importância de tower_diff
     deve crescer bastante de 10/15 min para 25 min (as placas só caem aos
     14 min); dragon_diff/gold_diff devem dominar em todas as fases.
  5. Checagem retrospectiva: rodando o modelo minuto a minuto em partidas
     REAIS (não sintéticas), a probabilidade média nos últimos minutos deve
     favorecer o time que de fato venceu, na maioria dos casos.

Uso:  python tests/validate_predictions.py
"""
import os
import sys

import joblib
import numpy as np
import pandas as pd
import shap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import get_conn
from src.features.build_features import CUTOFFS, features_from_timeline

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]

# ranges do 1º-99º percentil por fase (mesmos usados no front, matchState.ts)
RANGES = {
    10: {"gold_diff": 5500, "xp_diff": 4500, "kill_diff": 11, "tower_diff": 2, "dragon_diff": 1},
    15: {"gold_diff": 10000, "xp_diff": 9000, "kill_diff": 15, "tower_diff": 4, "dragon_diff": 2},
    20: {"gold_diff": 13500, "xp_diff": 12000, "kill_diff": 20, "tower_diff": 8, "dragon_diff": 3},
    25: {"gold_diff": 15000, "xp_diff": 16000, "kill_diff": 24, "tower_diff": 11, "dragon_diff": 4},
}

FAIL = []


def check(name: str, ok: bool, detail: str) -> None:
    status = "OK" if ok else "FALHA"
    print(f"[{status}] {name} — {detail}")
    if not ok:
        FAIL.append(name)


def predict(model, **feats) -> float:
    row = pd.DataFrame([[feats.get(f, 0) for f in FEATURES]], columns=FEATURES)
    return float(model.predict_proba(row)[0, 1])


def section1_monotonicity(models: dict) -> None:
    print("\n--- 1. Monotonicidade (mais vantagem nunca reduz a prob. do azul) ---")
    for cutoff in CUTOFFS:
        model = models[cutoff]
        r = RANGES[cutoff]
        for feat in FEATURES:
            xs = np.linspace(-r[feat], r[feat], 15)
            probs = [predict(model, **{feat: x}) for x in xs]
            # tolerância: árvores não são perfeitamente monotônicas ponto a
            # ponto, mas a correlação com a direção do ganho deve ser forte
            corr = np.corrcoef(xs, probs)[0, 1]
            check(
                f"corte {cutoff}min, {feat}",
                corr > 0.9,
                f"correlação prob×{feat} = {corr:.3f} (prob {probs[0]:.3f} -> {probs[-1]:.3f})",
            )


def section2_extremes(models: dict) -> None:
    print("\n--- 2. Casos extremos (vantagem/desvantagem total) ---")
    for cutoff in CUTOFFS:
        model = models[cutoff]
        r = RANGES[cutoff]
        lead = predict(model, **{f: r[f] for f in FEATURES})
        deficit = predict(model, **{f: -r[f] for f in FEATURES})
        check(f"corte {cutoff}min, liderança total", lead > 0.90, f"prob = {lead:.3f}")
        check(f"corte {cutoff}min, déficit total", deficit < 0.10, f"prob = {deficit:.3f}")
        check(
            f"corte {cutoff}min, simetria lead/deficit",
            abs((lead + deficit) - 1) < 0.05,
            f"lead {lead:.3f} + deficit {deficit:.3f} = {lead + deficit:.3f} (esperado ~1.0)",
        )


def section3_base_rate(models: dict) -> None:
    print("\n--- 3. Taxa-base por fase (tudo empatado — viés de lado esperado) ---")
    for cutoff in CUTOFFS:
        base = predict(models[cutoff])
        check(
            f"corte {cutoff}min, taxa-base < 50%",
            base < 0.50,
            f"prob = {base:.3f} (viés de lado documentado: vermelho favorecido)",
        )


def section4_shap_evolution(models: dict) -> None:
    print("\n--- 4. Evolução da importância SHAP entre fases ---")
    df = pd.read_csv("data/features_phases.csv")
    importances = {}
    for cutoff in CUTOFFS:
        part = df[df["cutoff_min"] == cutoff]
        X = part[FEATURES]
        explainer = shap.TreeExplainer(models[cutoff])
        vals = explainer(X)
        importances[cutoff] = {
            f: float(abs(vals.values[:, i]).mean()) for i, f in enumerate(FEATURES)
        }
    ratio = importances[25]["tower_diff"] / max(importances[10]["tower_diff"], 1e-9)
    check(
        "tower_diff cresce muito de 10 -> 25 min",
        ratio > 10,
        f"importância aos 10min={importances[10]['tower_diff']:.4f}, "
        f"aos 25min={importances[25]['tower_diff']:.4f} ({ratio:.0f}x)",
    )
    for cutoff in CUTOFFS:
        top = max(importances[cutoff], key=importances[cutoff].get)
        check(
            f"corte {cutoff}min, gold_diff ou dragon_diff domina",
            top in ("gold_diff", "dragon_diff"),
            f"fator mais importante = {top} ({importances[cutoff][top]:.4f})",
        )


def section5_retrospective(models: dict, sample_size: int = 30) -> None:
    print(f"\n--- 5. Checagem retrospectiva ({sample_size} partidas reais) ---")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT t.match_id, t.payload, tm.win
               FROM raw_timelines t
               JOIN teams tm ON tm.match_id = t.match_id AND tm.team_id = 100
               ORDER BY random() LIMIT %s""",
            (sample_size,),
        )
        rows = cur.fetchall()

    hits = 0
    total = 0
    for match_id, payload, blue_win in rows:
        frames = payload.get("info", {}).get("frames", [])
        n = len(frames)
        if n < 6:
            continue
        # média da probabilidade nos últimos 5 minutos disponíveis (antes do
        # fim), usando o modelo da fase correspondente a cada minuto
        last_minutes = range(max(1, n - 6), n - 1)
        probs = []
        for minute in last_minutes:
            feats = features_from_timeline(payload, minute)
            if feats is None:
                continue
            cutoff = max((c for c in CUTOFFS if c <= minute), default=min(CUTOFFS))
            probs.append(predict(models[cutoff], **feats))
        if not probs:
            continue
        avg_prob = sum(probs) / len(probs)
        predicted_blue = avg_prob >= 0.5
        total += 1
        if predicted_blue == blue_win:
            hits += 1

    rate = hits / total if total else 0
    check(
        "direção da predição bate com o vencedor real (últimos min.)",
        rate >= 0.70,
        f"{hits}/{total} partidas ({rate:.0%}) — nota: isto não é a acurácia "
        "formal do modelo (métricas de teste já reportadas), é uma checagem "
        "de sanidade rodando o pipeline completo (timeline real -> features "
        "-> modelo por fase) fora do pipeline de treino.",
    )


def main() -> None:
    models = joblib.load("data/models_phases.joblib")
    section1_monotonicity(models)
    section2_extremes(models)
    section3_base_rate(models)
    section4_shap_evolution(models)
    section5_retrospective(models)

    print(f"\n{'='*60}")
    if FAIL:
        print(f"{len(FAIL)} checagem(ns) falharam: {FAIL}")
    else:
        print("Todas as checagens passaram.")


if __name__ == "__main__":
    main()
