"""Features ricas de estado de jogo para os experimentos de precisão (12 a 16).

NÃO substitui `build_features.py` e não altera o modelo de produção nem os
números do TCC. Gera `data/features_v2.csv.gz` para
`src.models.experiment_precisao`.

Invariante 1 (vazamento): toda variável sai de `frames[: cutoff + 1]`.
Nada de estatística final, `winner` ou itens finalizados. O teste
`tests/test_features_v2_sem_vazamento.py` confere que cortar a timeline no
corte não muda nenhuma variável.

Base congelada: só as partidas que já estão em `data/features_phases.csv`
(as 39.426 do modelo de produção). A coleta em andamento (2026-11-03) não
entra, para os experimentos serem reprodutíveis e comparáveis ao 0,7621.

Uso:  python -m src.features.build_features_v2
"""
import os

import pandas as pd

from src.features.build_features import CUTOFFS, features_from_timeline

STATS = ["attackDamage", "abilityPower", "armor", "magicResist", "healthMax", "attackSpeed"]
MONSTERS = {"RIFTHERALD": "herald_diff", "BARON_NASHOR": "baron_diff", "HORDE": "grub_diff"}


def _team(pid: int) -> int:
    return 100 if int(pid) <= 5 else 200


def _gold_xp(frame: dict) -> tuple[int, int]:
    g = x = 0
    for pid, pf in frame.get("participantFrames", {}).items():
        s = 1 if _team(pid) == 100 else -1
        g += s * pf.get("totalGold", 0)
        x += s * pf.get("xp", 0)
    return g, x


def _kills_in(frames: list, a: int, b: int) -> int:
    """Diferença de abates (azul menos vermelho) nos quadros a..b inclusive."""
    d = 0
    for f in frames[a : b + 1]:
        for ev in f.get("events", []):
            if ev.get("type") == "CHAMPION_KILL" and ev.get("killerId", 0) > 0:
                d += 1 if ev["killerId"] <= 5 else -1
    return d


def rich_features(payload: dict, cutoff: int) -> dict | None:
    base = features_from_timeline(payload, cutoff)
    if base is None:
        return None
    frames = payload["info"]["frames"][: cutoff + 1]
    out = dict(base)

    # trajetória: ouro e experiência em minutos anteriores ao corte
    g_c, x_c = _gold_xp(frames[cutoff])
    for lag in (3, 5):
        k = max(cutoff - lag, 0)
        g_k, x_k = _gold_xp(frames[k])
        out[f"gold_d{lag}"] = g_c - g_k
        out[f"xp_d{lag}"] = x_c - x_k
        out[f"kill_d{lag}"] = _kills_in(frames, k + 1, cutoff)
    out["gold_5"] = _gold_xp(frames[5])[0] if cutoff >= 5 else 0
    out["gold_10"] = _gold_xp(frames[10])[0] if cutoff >= 10 else 0

    # por função (participantId i contra i+5), nível, farm, dano, atributos
    pfs = frames[cutoff].get("participantFrames", {})
    team_stat = {s: 0 for s in STATS}
    lvl = cs = jg = dmg = 0
    gmax = {100: 0, 200: 0}
    gmin = {100: 10**9, 200: 10**9}
    for i in range(1, 6):
        a, b = pfs.get(str(i), {}), pfs.get(str(i + 5), {})
        out[f"lane{i}_gold"] = a.get("totalGold", 0) - b.get("totalGold", 0)
        out[f"lane{i}_xp"] = a.get("xp", 0) - b.get("xp", 0)
        out[f"lane{i}_lvl"] = a.get("level", 0) - b.get("level", 0)
        cs_a = a.get("minionsKilled", 0) + a.get("jungleMinionsKilled", 0)
        cs_b = b.get("minionsKilled", 0) + b.get("jungleMinionsKilled", 0)
        out[f"lane{i}_cs"] = cs_a - cs_b
        da = a.get("damageStats", {}).get("totalDamageDoneToChampions", 0)
        db = b.get("damageStats", {}).get("totalDamageDoneToChampions", 0)
        out[f"lane{i}_dmg"] = da - db
        lvl += a.get("level", 0) - b.get("level", 0)
        cs += cs_a - cs_b
        jg += a.get("jungleMinionsKilled", 0) - b.get("jungleMinionsKilled", 0)
        dmg += da - db
        for s in STATS:
            team_stat[s] += a.get("championStats", {}).get(s, 0) - b.get("championStats", {}).get(s, 0)
        for t, pf in ((100, a), (200, b)):
            gmax[t] = max(gmax[t], pf.get("totalGold", 0))
            gmin[t] = min(gmin[t], pf.get("totalGold", 0))
    out.update(level_diff=lvl, cs_diff=cs, jungle_cs_diff=jg, dmg_diff=dmg)
    for s in STATS:
        out[f"stat_{s}"] = round(team_stat[s], 2)
    out["gold_max_diff"] = gmax[100] - gmax[200]
    out["gold_min_diff"] = gmin[100] - gmin[200]

    # objetivos e primeiros eventos (teamId em BUILDING_KILL/PLATE = dono)
    obj = {v: 0 for v in MONSTERS.values()}
    inhib = plates = 0
    first_blood = first_tower = 0
    for f in frames:
        for ev in f.get("events", []):
            t = ev.get("type")
            if t == "ELITE_MONSTER_KILL" and ev.get("monsterType") in MONSTERS:
                tm = ev.get("killerTeamId")
                if tm in (100, 200):
                    obj[MONSTERS[ev["monsterType"]]] += 1 if tm == 100 else -1
            elif t == "BUILDING_KILL":
                lost = ev.get("teamId")
                if lost in (100, 200):
                    win_team = 300 - lost
                    if ev.get("buildingType") == "INHIBITOR_BUILDING":
                        inhib += 1 if win_team == 100 else -1
                    if not first_tower and ev.get("buildingType") == "TOWER_BUILDING":
                        first_tower = 1 if win_team == 100 else -1
            elif t == "TURRET_PLATE_DESTROYED":
                dono = ev.get("teamId")
                if dono in (100, 200):
                    plates += 1 if dono == 200 else -1
            elif t == "CHAMPION_KILL" and not first_blood and ev.get("killerId", 0) > 0:
                first_blood = 1 if ev["killerId"] <= 5 else -1
    out.update(obj)
    out.update(inhib_diff=inhib, plate_diff=plates, first_blood=first_blood, first_tower=first_tower)
    return out


def main() -> None:
    from src.db import get_conn

    frozen = pd.read_csv("data/features_phases.csv", usecols=["match_id", "blue_win"]).drop_duplicates("match_id")
    ids = frozen["match_id"].tolist()
    win = dict(zip(frozen["match_id"], frozen["blue_win"]))
    print(f"{len(ids)} partidas na base congelada")

    conn = get_conn()
    rows = []
    with conn.cursor("tl2") as cur:
        cur.itersize = 100
        cur.execute("SELECT match_id, payload FROM raw_timelines WHERE match_id = ANY(%s)", (ids,))
        for n, (match_id, payload) in enumerate(cur, 1):
            for cutoff in CUTOFFS:
                f = rich_features(payload, cutoff)
                if f is None:
                    continue
                f.update(match_id=match_id, cutoff_min=cutoff, blue_win=int(win[match_id]))
                rows.append(f)
            if n % 5000 == 0:
                print(f"  {n} timelines")
    conn.close()

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/features_v2.csv.gz", index=False)
    print(f"{len(df)} linhas, {df.shape[1]} colunas -> data/features_v2.csv.gz")
    print(df.groupby("cutoff_min").size().to_dict())


if __name__ == "__main__":
    main()
