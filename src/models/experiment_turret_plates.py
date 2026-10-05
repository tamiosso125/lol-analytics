"""Experimento: placas de torre (TURRET_PLATE_DESTROYED) como feature nova
para o modelo de vitória — candidato achado em 2026-10-05 ao inspecionar o
payload bruto real (não a documentação) em busca de sinal ainda não
testado entre os 9 experimentos já registrados no Apêndice D do TCC.

Por que este é diferente dos 9 já testados: o SHAP por fase (Seção 5.4 do
TCC) mostra tower_diff quase zero antes dos 20 min porque TORRES RARAMENTE
MORREM cedo — mas as PLACAS de torre (bônus de ouro por dano à torre,
destruídas automaticamente aos 14 min) são batidas o jogo inteiro antes
disso, e nenhuma feature hoje enxerga esse sinal de pressão de rota
pré-14min. `TURRET_PLATE_DESTROYED` é um tipo de evento próprio na
timeline, nunca referenciado em build_features.py nem em nenhum dos 9
experimentos anteriores (confirmado por grep antes de escrever este
arquivo).

plate_diff = (placas destruídas pelo azul) - (pelo vermelho), até o corte.
Como as placas somem aos 14 min, só testado nos cortes 10 e 15 — nos
cortes 20/25 a feature satura (quase sempre o mesmo valor final) e não
teria por que ajudar.

Uso:  python -m src.models.experiment_turret_plates
"""
import json

import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from xgboost import XGBClassifier

from src.db import get_conn

ARTEFATO = "reports/experimento_placas_torre.json"

BASE_FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
CUTOFFS_RELEVANTES = (10, 15)  # placas somem aos 14min; 20/25 saturam


def plate_diff_by_cutoff(payload: dict) -> dict[int, int]:
    frames = payload.get("info", {}).get("frames", [])
    events = []  # (timestamp, teamId)
    for frame in frames:
        for ev in frame.get("events", []):
            if ev.get("type") == "TURRET_PLATE_DESTROYED":
                # teamId no evento é o time que SOFREU o dano (dono da torre),
                # não quem destruiu — mesma armadilha já documentada para
                # killerTeamId em ELITE_MONSTER_KILL (ver diario_execucao.md,
                # 2026-07-08). O time que GANHA ouro é o time OPOSTO ao dono.
                dono = ev.get("teamId")
                if dono in (100, 200):
                    beneficiario = 200 if dono == 100 else 100
                    events.append((ev.get("timestamp", 0), beneficiario))

    out = {}
    for cutoff in CUTOFFS_RELEVANTES:
        if len(frames) <= cutoff:
            continue
        cutoff_ms = cutoff * 60_000
        count = {100: 0, 200: 0}
        for ts, team in events:
            if ts <= cutoff_ms:
                count[team] += 1
        out[cutoff] = count[100] - count[200]
    return out


def build_experiment_df() -> pd.DataFrame:
    rows = []
    with get_conn() as conn, conn.cursor("tl_plates_exp") as cur:
        cur.itersize = 100
        cur.execute(
            """SELECT t.match_id, t.payload, tm.win
               FROM raw_timelines t
               JOIN teams tm ON tm.match_id = t.match_id AND tm.team_id = 100"""
        )
        for match_id, payload, blue_win in cur:
            diffs = plate_diff_by_cutoff(payload)
            for cutoff, plate_diff in diffs.items():
                rows.append({"match_id": match_id, "cutoff_min": cutoff, "plate_diff": plate_diff})
    df = pd.DataFrame(rows)
    print(f"{len(df)} linhas (match x cutoff) com plate_diff calculado.")
    print(f"distribuicao plate_diff (corte 15min): "
          f"{df[df.cutoff_min==15]['plate_diff'].describe().to_dict()}")
    return df


def compare(configs: dict[str, pd.DataFrame], y: pd.Series, label: str) -> dict:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["roc_auc", "accuracy"]
    model = XGBClassifier(n_estimators=300, learning_rate=0.05, eval_metric="logloss", random_state=42)

    print(f"\n[{label}] n={len(y)}")
    print(f"{'':<28} {'AUC-ROC':>10} {'Acurácia':>10}")
    base_auc = None
    resultado = {}
    for name, X in configs.items():
        res = cross_validate(model, X, y, cv=cv, scoring=scoring)
        auc = res["test_roc_auc"].mean()
        acc = res["test_accuracy"].mean()
        if base_auc is None:
            base_auc = auc
        delta = auc - base_auc
        print(
            f"{name:<28} {auc:>10.4f} {acc:>10.4f}"
            + (f"   (delta {delta:+.4f})" if name != "baseline (5 features)" else "")
        )
        resultado[name] = {"auc": round(auc, 4), "acuracia": round(acc, 4), "delta_auc": round(delta, 4)}
    return resultado


def main() -> None:
    df_phases = pd.read_csv("data/features_phases.csv")
    df_plates = build_experiment_df()

    artefato = {
        "hipotese": (
            "TURRET_PLATE_DESTROYED (evento da timeline nunca testado) como "
            "feature plate_diff — candidato a preencher a janela onde "
            "tower_diff fica ~0 porque torres raramente morrem antes dos "
            "15min, mas placas sao batidas o jogo inteiro nessa janela."
        ),
        "n_linhas_match_x_cutoff": len(df_plates),
        "cortes": {},
    }

    for cutoff in CUTOFFS_RELEVANTES:
        merged = df_phases[df_phases["cutoff_min"] == cutoff].merge(
            df_plates[df_plates["cutoff_min"] == cutoff][["match_id", "plate_diff"]],
            on="match_id",
            how="inner",
        )
        if len(merged) < 200:
            print(f"\ncorte {cutoff} min: amostra pequena demais ({len(merged)}), pulando.")
            continue
        y = merged["blue_win"]
        configs = {
            "baseline (5 features)": merged[BASE_FEATURES],
            "+ plate_diff": merged[BASE_FEATURES + ["plate_diff"]],
        }
        resultado = compare(configs, y, label=f"corte {cutoff} min")
        artefato["cortes"][str(cutoff)] = {"n": len(merged), **resultado}

    with open(ARTEFATO, "w", encoding="utf-8") as f:
        json.dump(artefato, f, indent=2, ensure_ascii=False)
    print(f"\nartefato gravado: {ARTEFATO}")


if __name__ == "__main__":
    main()
