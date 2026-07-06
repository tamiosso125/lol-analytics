"""Experimento: item_gold_diff como feature nova para o modelo de vitória.

Hipótese (pendente registrada em docs/diario_execucao.md 2026-07-05):
barão/arauto, dispersão de time, tuning por fase e calibração já foram
testados e não renderam ganho sobre gold_diff/xp_diff/kill_diff/
tower_diff/dragon_diff. Itens finalizados (Zhonya's, Rabadon's etc.)
capturam poder de combate que gold_diff sozinho não distingue: dois
times com o mesmo gold_diff podem estar em estágios de build muito
diferentes (componentes espalhados vs. um item completo).

feature: item_gold_diff = valor em ouro (total_gold do Data Dragon) dos
itens "finalizados" (mesmo filtro de _completed_item_ids em
src/api/main.py: não é componente de nada, comprável, custo >= 1100,
não é consumível/trinket, válido no mapa 11) que cada time ainda
possui no corte de tempo (compras menos vendas do mesmo item,
ITEM_UNDO desfazendo a ação mais recente — mesma lógica de
src/etl/load_items.py, mas aqui por participantId dentro da própria
timeline, sem precisar de join com item_events/participants).

Não mexe em build_features.py/features.csv nem no modelo em produção
— roda isolado, mede o ganho (ou a falta dele) e só then decide se
vale integrar de verdade.

Uso:  python -m src.models.experiment_item_gold
"""
import json

import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from xgboost import XGBClassifier

from src.features.build_features import CUTOFFS
from src.db import get_conn

ITEMS_PATH = "data/items.json"
BASE_FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]


def _completed_item_gold() -> dict[int, int]:
    with open(ITEMS_PATH, encoding="utf-8") as f:
        items = json.load(f)
    out = {}
    for iid, it in items.items():
        if (
            not it.get("into")
            and it.get("purchasable")
            and it.get("total_gold", 0) >= 1100
            and not ({"Consumable", "Trinket"} & set(it.get("tags", [])))
            and it.get("maps", {}).get("11")
        ):
            out[int(iid)] = it.get("total_gold", 0)
    return out


def item_gold_diff_by_cutoff(payload: dict, item_gold: dict[int, int]) -> dict[int, int]:
    """{cutoff_min: item_gold_diff} — valor líquido (compra-venda, com
    UNDO desfeito) dos itens finalizados possuídos por cada participante,
    somado por time (100/200), diferença azul-vermelho, por corte."""
    frames = payload.get("info", {}).get("frames", [])
    # eventos por participante em ordem, pra poder desfazer o mais recente
    per_pid: dict[int, list[list]] = {}
    for frame in frames:
        for ev in frame.get("events", []):
            t = ev.get("type")
            pid = ev.get("participantId")
            if not pid or pid == 0:
                continue
            events = per_pid.setdefault(pid, [])
            if t == "ITEM_PURCHASED":
                events.append(["BUY", ev.get("timestamp", 0), ev.get("itemId")])
            elif t == "ITEM_SOLD":
                events.append(["SELL", ev.get("timestamp", 0), ev.get("itemId")])
            elif t == "ITEM_UNDO":
                target_action, target_item = (
                    ("BUY", ev.get("beforeId")) if ev.get("beforeId") else ("SELL", ev.get("afterId"))
                )
                for i in range(len(events) - 1, -1, -1):
                    if events[i][0] == target_action and events[i][2] == target_item:
                        del events[i]
                        break

    out = {}
    for cutoff in CUTOFFS:
        if len(frames) <= cutoff:
            continue
        cutoff_ms = cutoff * 60_000
        gold = {100: 0, 200: 0}
        for pid, events in per_pid.items():
            team = 100 if pid <= 5 else 200
            for action, ts, item_id in events:
                if ts > cutoff_ms or item_id not in item_gold:
                    continue
                gold[team] += item_gold[item_id] if action == "BUY" else -item_gold[item_id]
        out[cutoff] = gold[100] - gold[200]
    return out


def build_experiment_df() -> pd.DataFrame:
    item_gold = _completed_item_gold()
    print(f"{len(item_gold)} itens finalizados no catálogo (>= 1100 ouro).")

    rows = []
    with get_conn() as conn, conn.cursor("tl_item_exp") as cur:
        cur.itersize = 100
        cur.execute(
            """SELECT t.match_id, t.payload, tm.win
               FROM raw_timelines t
               JOIN teams tm ON tm.match_id = t.match_id AND tm.team_id = 100"""
        )
        for match_id, payload, blue_win in cur:
            diffs = item_gold_diff_by_cutoff(payload, item_gold)
            for cutoff, diff in diffs.items():
                rows.append({"match_id": match_id, "cutoff_min": cutoff, "item_gold_diff": diff})
    df = pd.DataFrame(rows)
    print(f"{len(df)} linhas (match x cutoff) com item_gold_diff calculado.")
    return df


def compare(X_base: pd.DataFrame, X_with: pd.DataFrame, y: pd.Series, label: str) -> None:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["roc_auc", "accuracy"]
    model = XGBClassifier(n_estimators=300, learning_rate=0.05, eval_metric="logloss", random_state=42)

    res_base = cross_validate(model, X_base, y, cv=cv, scoring=scoring)
    res_with = cross_validate(model, X_with, y, cv=cv, scoring=scoring)

    print(f"\n[{label}] n={len(y)}")
    print(f"{'':<28} {'AUC-ROC':>10} {'Acurácia':>10}")
    print(f"{'baseline (5 features)':<28} {res_base['test_roc_auc'].mean():>10.4f} {res_base['test_accuracy'].mean():>10.4f}")
    print(f"{'+ item_gold_diff (6)':<28} {res_with['test_roc_auc'].mean():>10.4f} {res_with['test_accuracy'].mean():>10.4f}")
    delta_auc = res_with["test_roc_auc"].mean() - res_base["test_roc_auc"].mean()
    print(f"delta AUC-ROC: {delta_auc:+.4f}")


def main() -> None:
    df_phases = pd.read_csv("data/features_phases.csv")
    df_item = build_experiment_df()

    for cutoff in CUTOFFS:
        merged = df_phases[df_phases["cutoff_min"] == cutoff].merge(
            df_item[df_item["cutoff_min"] == cutoff][["match_id", "item_gold_diff"]],
            on="match_id",
            how="inner",  # só partidas com timeline+item coverage nos dois lados
        )
        if len(merged) < 200:
            print(f"\ncorte {cutoff} min: amostra pequena demais ({len(merged)}), pulando.")
            continue
        y = merged["blue_win"]
        X_base = merged[BASE_FEATURES]
        X_with = merged[BASE_FEATURES + ["item_gold_diff"]]
        compare(X_base, X_with, y, label=f"corte {cutoff} min")


if __name__ == "__main__":
    main()
