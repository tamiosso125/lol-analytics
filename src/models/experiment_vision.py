"""Experimento: visão (WARD_PLACED/WARD_KILL) como feature nova para o
modelo de vitória — último candidato de dado novo pendente (ver
docs/diario_execucao.md; item_gold_diff já testado em 2026-07-06,
negativo).

Duas features candidatas, ambas na mesma convenção dos diffs já
existentes (positivo = vantagem azul):

  ward_diff      = (wards colocadas pelo azul) - (pelo vermelho), até o
                   corte. Proxy de controle de visão/mapa — times à
                   frente costumam colocar mais controle wards pra
                   proteger objetivos.
  ward_kill_diff = (wards inimigas destruídas pelo azul) - (pelo
                   vermelho), até o corte. Proxy de agressividade de
                   contra-visão (dewarding).

creatorId/killerId == 0 é filtrado (evento de sistema, mesmo padrão de
participantId==0 nos itens/abates). Testa cada feature isolada e as
duas juntas, nos 4 cortes — não mexe em build_features.py/modelo em
produção.

Uso:  python -m src.models.experiment_vision
"""
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from xgboost import XGBClassifier

from src.features.build_features import CUTOFFS
from src.db import get_conn

BASE_FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]


def vision_diffs_by_cutoff(payload: dict) -> dict[int, dict[str, int]]:
    frames = payload.get("info", {}).get("frames", [])
    # (timestamp, team) por evento, separado por tipo — soma acumulada até o corte
    placed = []  # (ts, team)
    killed = []
    for frame in frames:
        for ev in frame.get("events", []):
            t = ev.get("type")
            if t == "WARD_PLACED":
                pid = ev.get("creatorId", 0)
                if pid and pid > 0:
                    placed.append((ev.get("timestamp", 0), 100 if pid <= 5 else 200))
            elif t == "WARD_KILL":
                pid = ev.get("killerId", 0)
                if pid and pid > 0:
                    killed.append((ev.get("timestamp", 0), 100 if pid <= 5 else 200))

    out = {}
    for cutoff in CUTOFFS:
        if len(frames) <= cutoff:
            continue
        cutoff_ms = cutoff * 60_000
        p = {100: 0, 200: 0}
        for ts, team in placed:
            if ts <= cutoff_ms:
                p[team] += 1
        k = {100: 0, 200: 0}
        for ts, team in killed:
            if ts <= cutoff_ms:
                k[team] += 1
        out[cutoff] = {
            "ward_diff": p[100] - p[200],
            "ward_kill_diff": k[100] - k[200],
        }
    return out


def build_experiment_df() -> pd.DataFrame:
    rows = []
    with get_conn() as conn, conn.cursor("tl_vision_exp") as cur:
        cur.itersize = 100
        cur.execute(
            """SELECT t.match_id, t.payload, tm.win
               FROM raw_timelines t
               JOIN teams tm ON tm.match_id = t.match_id AND tm.team_id = 100"""
        )
        for match_id, payload, blue_win in cur:
            diffs = vision_diffs_by_cutoff(payload)
            for cutoff, feats in diffs.items():
                rows.append({"match_id": match_id, "cutoff_min": cutoff, **feats})
    df = pd.DataFrame(rows)
    print(f"{len(df)} linhas (match x cutoff) com ward_diff/ward_kill_diff calculados.")
    return df


def compare(configs: dict[str, pd.DataFrame], y: pd.Series, label: str) -> None:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["roc_auc", "accuracy"]
    model = XGBClassifier(n_estimators=300, learning_rate=0.05, eval_metric="logloss", random_state=42)

    print(f"\n[{label}] n={len(y)}")
    print(f"{'':<28} {'AUC-ROC':>10} {'Acurácia':>10}")
    base_auc = None
    for name, X in configs.items():
        res = cross_validate(model, X, y, cv=cv, scoring=scoring)
        auc = res["test_roc_auc"].mean()
        if base_auc is None:
            base_auc = auc
        delta = auc - base_auc
        print(
            f"{name:<28} {auc:>10.4f} {res['test_accuracy'].mean():>10.4f}"
            + (f"   (delta {delta:+.4f})" if name != "baseline (5 features)" else "")
        )


def main() -> None:
    df_phases = pd.read_csv("data/features_phases.csv")
    df_vision = build_experiment_df()

    for cutoff in CUTOFFS:
        merged = df_phases[df_phases["cutoff_min"] == cutoff].merge(
            df_vision[df_vision["cutoff_min"] == cutoff][["match_id", "ward_diff", "ward_kill_diff"]],
            on="match_id",
            how="inner",
        )
        if len(merged) < 200:
            print(f"\ncorte {cutoff} min: amostra pequena demais ({len(merged)}), pulando.")
            continue
        y = merged["blue_win"]
        configs = {
            "baseline (5 features)": merged[BASE_FEATURES],
            "+ ward_diff": merged[BASE_FEATURES + ["ward_diff"]],
            "+ ward_kill_diff": merged[BASE_FEATURES + ["ward_kill_diff"]],
            "+ ambas": merged[BASE_FEATURES + ["ward_diff", "ward_kill_diff"]],
        }
        compare(configs, y, label=f"corte {cutoff} min")


if __name__ == "__main__":
    main()
