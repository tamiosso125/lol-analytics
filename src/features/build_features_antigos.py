"""Variáveis dos experimentos 2, 5/7, 8 e 9, refeitas na base congelada.

Os onze primeiros experimentos de enriquecimento (Quadro 5 da Seção 5.4) foram
medidos antes do protocolo dos experimentos 12 a 19: bases de tamanhos
diferentes, sem intervalo de confiança. Este módulo recalcula as variáveis que
faltavam, na mesma base de 39.426 partidas, para `experiment_antigos.py` medir
todas com o mesmo protocolo (2026-11-04).

NÃO altera o modelo de produção, o `data/features.csv` nem os números do TCC.

Invariante 1 (vazamento): toda variável sai de `frames[: cutoff + 1]`. O teste
`tests/test_features_antigos_sem_vazamento.py` confere que cortar a timeline no
corte não muda nenhuma variável. As funções antigas
(`experiment_item_gold`, `experiment_vision`) olhavam a timeline inteira e
filtravam por timestamp; aqui o corte é estrutural, nos quadros.

Variáveis (todas azul menos vermelho):
  spread_diff       dispersão espacial: distância média dos 5 jogadores ao
                    centro do próprio time, no quadro do corte (experimento 2)
  item_gold_diff    valor em ouro dos itens finalizados que cada time possui no
                    corte, compras menos vendas, com ITEM_UNDO desfeito
                    (experimentos 5 e 7)
  ward_diff         sentinelas colocadas até o corte (experimento 8)
  ward_kill_diff    sentinelas inimigas destruídas até o corte (experimento 8)
  drag_<tipo>_diff  dragões por tipo (monsterSubType) até o corte
                    (experimento 9)

Uso:  python -m src.features.build_features_antigos
"""
import json
import os

import pandas as pd

from src.features.build_features import CUTOFFS

ITEMS_PATH = "data/items.json"
DRAGOES = ["FIRE", "WATER", "EARTH", "AIR", "HEXTECH", "CHEMTECH", "ELDER"]
SAIDA = "data/features_antigos.csv.gz"


def _team(pid: int) -> int:
    return 100 if int(pid) <= 5 else 200


def itens_finalizados() -> dict[int, int]:
    """Mesmo filtro de `experiment_item_gold._completed_item_gold`: não é
    componente, é comprável, custa >= 1100, não é consumível nem item de
    visão e vale no mapa 11."""
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


def _spread(frame: dict) -> dict[int, float]:
    pts = {100: [], 200: []}
    for pid, pf in frame.get("participantFrames", {}).items():
        pos = pf.get("position")
        if pos and "x" in pos and "y" in pos:
            pts[_team(pid)].append((pos["x"], pos["y"]))
    out = {}
    for t, p in pts.items():
        if not p:
            out[t] = 0.0
            continue
        cx = sum(x for x, _ in p) / len(p)
        cy = sum(y for _, y in p) / len(p)
        out[t] = sum(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 for x, y in p) / len(p)
    return out


def antigos_features(payload: dict, cutoff: int, item_gold: dict[int, int]) -> dict | None:
    frames_all = payload.get("info", {}).get("frames", [])
    if len(frames_all) <= cutoff:
        return None
    frames = frames_all[: cutoff + 1]
    out: dict = {}

    sp = _spread(frames[cutoff])
    out["spread_diff"] = round(sp[100] - sp[200], 2)

    per_pid: dict[int, list[list]] = {}
    placed = {100: 0, 200: 0}
    killed = {100: 0, 200: 0}
    drag = {k: 0 for k in DRAGOES}
    for f in frames:
        for ev in f.get("events", []):
            t = ev.get("type")
            if t in ("ITEM_PURCHASED", "ITEM_SOLD", "ITEM_UNDO"):
                pid = ev.get("participantId")
                if not pid:
                    continue
                evs = per_pid.setdefault(pid, [])
                if t == "ITEM_PURCHASED":
                    evs.append(["BUY", ev.get("itemId")])
                elif t == "ITEM_SOLD":
                    evs.append(["SELL", ev.get("itemId")])
                else:
                    acao, alvo = ("BUY", ev.get("beforeId")) if ev.get("beforeId") else ("SELL", ev.get("afterId"))
                    for i in range(len(evs) - 1, -1, -1):
                        if evs[i][0] == acao and evs[i][1] == alvo:
                            del evs[i]
                            break
            elif t == "WARD_PLACED":
                pid = ev.get("creatorId", 0)
                if pid and pid > 0:
                    placed[_team(pid)] += 1
            elif t == "WARD_KILL":
                pid = ev.get("killerId", 0)
                if pid and pid > 0:
                    killed[_team(pid)] += 1
            elif t == "ELITE_MONSTER_KILL" and ev.get("monsterType") == "DRAGON":
                tipo = str(ev.get("monsterSubType", "")).replace("_DRAGON", "")
                tm = ev.get("killerTeamId")
                if tipo in drag and tm in (100, 200):
                    drag[tipo] += 1 if tm == 100 else -1

    gold = {100: 0, 200: 0}
    for pid, evs in per_pid.items():
        for acao, item_id in evs:
            if item_id in item_gold:
                gold[_team(pid)] += item_gold[item_id] if acao == "BUY" else -item_gold[item_id]
    out["item_gold_diff"] = gold[100] - gold[200]
    out["ward_diff"] = placed[100] - placed[200]
    out["ward_kill_diff"] = killed[100] - killed[200]
    for k, v in drag.items():
        out[f"drag_{k.lower()}_diff"] = v
    return out


def main() -> None:
    from src.db import get_conn

    frozen = pd.read_csv("data/features_phases.csv", usecols=["match_id"]).drop_duplicates("match_id")
    ids = frozen["match_id"].tolist()
    item_gold = itens_finalizados()
    print(f"{len(ids)} partidas na base congelada; {len(item_gold)} itens finalizados no catálogo")

    rows = []
    conn = get_conn()
    with conn.cursor("tl_antigos") as cur:
        cur.itersize = 100
        cur.execute("SELECT match_id, payload FROM raw_timelines WHERE match_id = ANY(%s)", (ids,))
        for n, (match_id, payload) in enumerate(cur, 1):
            for cutoff in CUTOFFS:
                f = antigos_features(payload, cutoff, item_gold)
                if f is None:
                    continue
                f.update(match_id=match_id, cutoff_min=cutoff)
                rows.append(f)
            if n % 5000 == 0:
                print(f"  {n} timelines", flush=True)
    conn.close()

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv(SAIDA, index=False)
    print(f"{len(df)} linhas, {df.shape[1]} colunas -> {SAIDA}")
    print(df.groupby("cutoff_min").size().to_dict())


if __name__ == "__main__":
    main()
