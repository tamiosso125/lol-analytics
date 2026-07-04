"""Features para predição de vitória (nível de time).

ATENÇÃO — vazamento de dados (data leakage): estatísticas finais da
partida (kills, gold total etc.) "preveem" a vitória trivialmente.
Para o TCC, defina explicitamente a tarefa:

  A) Pré-jogo: prever vitória a partir da composição (campeões/posições)
     e histórico dos jogadores — usa apenas dados disponíveis antes do jogo.
  B) Em jogo: prever vitória com o estado da partida em um corte de
     tempo (diferença de ouro/XP/objetivos), extraído de raw_timelines,
     como em Hodge et al. (2021).

Este módulo implementa a opção B com frames da timeline em MÚLTIPLOS
cortes (fases do jogo):
  10 min = fase de rotas; 15 = fim das rotas (placas caem aos 14);
  20 = mid game; 25 = transição para o late game.

Uso:  python -m src.features.build_features
Gera: data/features_phases.csv (todos os cortes, coluna cutoff_min)
      data/features.csv        (somente o corte de 15 min — compatível
                                com train_baseline/tune_models/gold15)
"""
import os

import pandas as pd

MINUTE_MS = 60_000
CUTOFF_MIN = 15  # corte padrão (fim da fase de rotas)
CUTOFFS = [10, 15, 20, 25]


def features_from_timeline(payload: dict, cutoff_min: int = CUTOFF_MIN) -> dict | None:
    frames = payload.get("info", {}).get("frames", [])
    if len(frames) <= cutoff_min:
        return None  # partida acabou antes do corte
    frame = frames[cutoff_min]

    gold = {100: 0, 200: 0}
    xp = {100: 0, 200: 0}
    for pid, pf in frame.get("participantFrames", {}).items():
        team = 100 if int(pid) <= 5 else 200
        gold[team] += pf.get("totalGold", 0)
        xp[team] += pf.get("xp", 0)

    kills = {100: 0, 200: 0}
    towers = {100: 0, 200: 0}
    dragons = {100: 0, 200: 0}
    for f in frames[: cutoff_min + 1]:
        for ev in f.get("events", []):
            t = ev.get("type")
            if t == "CHAMPION_KILL":
                team = 100 if ev.get("killerId", 0) <= 5 else 200
                if ev.get("killerId", 0) > 0:
                    kills[team] += 1
            elif t == "BUILDING_KILL":
                # killerTeamId no evento é o time que PERDEU a torre
                lost = ev.get("teamId")
                if lost in (100, 200):
                    towers[300 - lost] += 1
            elif t == "ELITE_MONSTER_KILL" and ev.get("monsterType") == "DRAGON":
                team = ev.get("killerTeamId")
                if team in (100, 200):
                    dragons[team] += 1

    return {
        "gold_diff": gold[100] - gold[200],
        "xp_diff": xp[100] - xp[200],
        "kill_diff": kills[100] - kills[200],
        "tower_diff": towers[100] - towers[200],
        "dragon_diff": dragons[100] - dragons[200],
    }


def main() -> None:
    from src.db import get_conn

    conn = get_conn()
    rows = []
    with conn.cursor("tl") as cur:
        cur.itersize = 100
        cur.execute(
            """SELECT t.match_id, t.payload, tm.win
               FROM raw_timelines t
               JOIN teams tm ON tm.match_id = t.match_id AND tm.team_id = 100"""
        )
        for match_id, payload, blue_win in cur:
            for cutoff in CUTOFFS:
                feats = features_from_timeline(payload, cutoff)
                if feats is None:
                    continue
                feats["match_id"] = match_id
                feats["cutoff_min"] = cutoff
                feats["blue_win"] = int(blue_win)
                rows.append(feats)
    conn.close()

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/features_phases.csv", index=False)
    # corte padrão separado, sem a coluna cutoff_min (compatibilidade)
    df15 = df[df["cutoff_min"] == CUTOFF_MIN].drop(columns=["cutoff_min"])
    df15.to_csv("data/features.csv", index=False)
    per_cutoff = df.groupby("cutoff_min").size().to_dict()
    print(f"{len(df)} linhas -> data/features_phases.csv  (por corte: {per_cutoff})")
    print(f"{len(df15)} partidas -> data/features.csv (corte de {CUTOFF_MIN} min)")


if __name__ == "__main__":
    main()
