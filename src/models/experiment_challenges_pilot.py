"""Piloto (Fase 1 do plano de 2026-10-05): lol-challenges-v1 como feature
nova — teamwork_pct_diff / expertise_pct_diff, agregados por time a partir
do percentil de cada jogador nas categorias TEAMWORK e EXPERTISE.

POR QUE SÓ ISSO E NÃO champion-mastery-v4: mastery é redundante com o
shrinkage de WR-por-campeão que já existe (ambos aproximam "familiaridade
com o campeão", shrinkage é baseado em resultado, mastery só em volume) e
é um sinal comprimido na nossa população (Challenger/GM/Master já jogou
muito os campeões que joga). TEAMWORK/EXPERTISE são eixo que não existe em
nenhuma feature já testada — candidato genuinamente novo, não variação dos
anteriores.

POR QUE É SÓ PILOTO, NÃO EXPERIMENTO DEFINITIVO: lol-challenges-v1 devolve
o estado VITALÍCIO ATUAL do jogador, não o estado dele na época de uma
partida passada — aplicar isso ao histórico tem risco de vazamento. Este
script MEDE o gap (data da partida x data da consulta) em vez de ignorá-lo
ou supor que é pequeno. Usa as partidas MAIS RECENTES da KR (a região com
menor gap no banco) para minimizar o problema.

POR QUE NÃO USA data/features_phases.csv: esse arquivo é o snapshot
CONGELADO que o TCC já documenta e verifica (39.188/39.426 partidas,
Seção 5.8: "o modelo não viu a última rodada de coleta" é decisão
deliberada). As partidas mais recentes da KR usadas aqui são posteriores a
esse congelamento — por isso as 5 features-base são recalculadas aqui,
direto de raw_timelines, via a MESMA função de produção
(features_from_timeline), sem tocar no arquivo congelado nem nos números
já verificados do TCC.

Uso:  python -m src.models.experiment_challenges_pilot [--n-matches 200]
      (reusa reports/_cache_challenges_kr.json se já existir, não reconsulta
      jogador já respondido — relançar após uma falha parcial é barato)
"""
import argparse
import json
import os
from datetime import datetime, timezone

import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from xgboost import XGBClassifier

from src.db import get_conn
from src.features.build_features import features_from_timeline
from src.riot.client import RiotClient

ARTEFATO = "reports/experimento_challenges_piloto.json"
CACHE = "reports/_cache_challenges_kr.json"
BASE_FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
CUTOFF = 15


def partidas_recentes_kr(n: int) -> list[dict]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT m.match_id, m.game_creation
               FROM matches m
               WHERE m.platform_id = 'KR' AND m.queue_id = 420
               ORDER BY m.game_creation DESC
               LIMIT %s""",
            (n,),
        )
        return [{"match_id": r[0], "game_creation": r[1]} for r in cur.fetchall()]


def participantes(match_ids: list[str]) -> pd.DataFrame:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT match_id, puuid, team_id
               FROM participants
               WHERE match_id = ANY(%s)""",
            (match_ids,),
        )
        return pd.DataFrame(cur.fetchall(), columns=["match_id", "puuid", "team_id"])


def features_base(match_ids: list[str]) -> pd.DataFrame:
    """Recalcula as 5 features-base direto de raw_timelines (corte 15min) +
    win do time azul, SEM depender do features_phases.csv congelado."""
    rows = []
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT t.match_id, t.payload, tm.win
               FROM raw_timelines t
               JOIN teams tm ON tm.match_id = t.match_id AND tm.team_id = 100
               WHERE t.match_id = ANY(%s)""",
            (match_ids,),
        )
        for match_id, payload, blue_win in cur:
            feats = features_from_timeline(payload, cutoff_min=CUTOFF)
            if feats is None:
                continue
            rows.append({"match_id": match_id, "blue_win": blue_win, **feats})
    return pd.DataFrame(rows)


def coletar_challenges(puuids: list[str], client: RiotClient) -> dict[str, dict]:
    cache: dict[str, dict] = {}
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            cache = json.load(f)
        print(f"cache encontrado: {len(cache)} jogadores ja consultados antes")

    faltam = [p for p in puuids if p not in cache]
    print(f"{len(faltam)} jogadores novos a consultar (de {len(puuids)} pedidos)")
    for i, puuid in enumerate(faltam, 1):
        try:
            data = client.challenges_by_puuid(puuid)
            cat = data.get("categoryPoints", {})
            cache[puuid] = {
                "teamwork_pct": cat.get("TEAMWORK", {}).get("percentile"),
                "expertise_pct": cat.get("EXPERTISE", {}).get("percentile"),
            }
        except Exception as exc:
            print(f"  [{i}/{len(faltam)}] erro em {puuid[:12]}...: {exc}")
        if i % 100 == 0:
            print(f"  [{i}/{len(faltam)}] consultados; salvando cache parcial")
            with open(CACHE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False)

    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    return {p: cache[p] for p in puuids if p in cache}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-matches", type=int, default=200)
    args = ap.parse_args()

    agora = datetime.now(timezone.utc)
    partidas = partidas_recentes_kr(args.n_matches)
    match_ids = [p["match_id"] for p in partidas]
    gaps_dias = [(agora - p["game_creation"]).days for p in partidas]
    print(f"{len(partidas)} partidas KR selecionadas | gap em dias: "
          f"min={min(gaps_dias)} max={max(gaps_dias)} "
          f"media={sum(gaps_dias)/len(gaps_dias):.1f}")

    df_part = participantes(match_ids)
    puuids_unicos = df_part["puuid"].unique().tolist()
    print(f"{len(puuids_unicos)} jogadores unicos a consultar (lol-challenges-v1)")

    client = RiotClient(platform="kr")
    challenges = coletar_challenges(puuids_unicos, client)
    print(f"{len(challenges)}/{len(puuids_unicos)} consultas OK (cache + novas)")

    df_part["teamwork_pct"] = df_part["puuid"].map(lambda p: challenges.get(p, {}).get("teamwork_pct"))
    df_part["expertise_pct"] = df_part["puuid"].map(lambda p: challenges.get(p, {}).get("expertise_pct"))

    agg = (
        df_part.dropna(subset=["teamwork_pct", "expertise_pct"])
        .groupby(["match_id", "team_id"])[["teamwork_pct", "expertise_pct"]]
        .mean()
        .reset_index()
    )
    contagem = df_part.groupby(["match_id", "team_id"]).size().reset_index(name="n")
    times_completos = set(
        tuple(x) for x in contagem[contagem["n"] == 5][["match_id", "team_id"]].values
    )
    agg = agg[agg.apply(lambda r: (r["match_id"], r["team_id"]) in times_completos, axis=1)]

    azul = agg[agg.team_id == 100].set_index("match_id")
    vermelho = agg[agg.team_id == 200].set_index("match_id")
    diffs = (azul[["teamwork_pct", "expertise_pct"]] - vermelho[["teamwork_pct", "expertise_pct"]]).dropna()
    diffs = diffs.rename(columns={"teamwork_pct": "teamwork_pct_diff", "expertise_pct": "expertise_pct_diff"})
    diffs = diffs.reset_index()
    print(f"{len(diffs)} partidas com os dois times completos (5+5 com challenges resolvido)")

    df_base = features_base(match_ids)
    print(f"{len(df_base)} partidas com features-base recalculadas de raw_timelines (corte {CUTOFF}min)")

    merged = df_base.merge(diffs, on="match_id", how="inner")
    print(f"{len(merged)} partidas apos merge features-base x challenges")

    artefato = {
        "regiao": "KR",
        "n_partidas_selecionadas": len(partidas),
        "gap_dias": {"min": min(gaps_dias), "max": max(gaps_dias),
                     "media": round(sum(gaps_dias) / len(gaps_dias), 1)},
        "n_jogadores_unicos": len(puuids_unicos),
        "n_challenges_ok": len(challenges),
        "n_partidas_times_completos": len(diffs),
        "n_partidas_teste_final": len(merged),
    }

    if len(merged) < 100:
        artefato["veredito"] = "amostra pequena demais para medir, apenas piloto de viabilidade"
        print(f"\nAmostra final pequena demais ({len(merged)}) para um teste confiavel.")
    else:
        y = merged["blue_win"]
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scoring = ["roc_auc", "accuracy"]
        model = XGBClassifier(n_estimators=300, learning_rate=0.05, eval_metric="logloss", random_state=42)
        configs = {
            "baseline (5 features)": merged[BASE_FEATURES],
            "+ teamwork_pct_diff": merged[BASE_FEATURES + ["teamwork_pct_diff"]],
            "+ expertise_pct_diff": merged[BASE_FEATURES + ["expertise_pct_diff"]],
            "+ ambas": merged[BASE_FEATURES + ["teamwork_pct_diff", "expertise_pct_diff"]],
        }
        print(f"\n[corte {CUTOFF}min] n={len(y)}")
        print(f"{'':<28} {'AUC-ROC':>10} {'Acuracia':>10}")
        base_auc = None
        resultado = {}
        for name, X in configs.items():
            res = cross_validate(model, X, y, cv=cv, scoring=scoring)
            auc = res["test_roc_auc"].mean()
            acc = res["test_accuracy"].mean()
            if base_auc is None:
                base_auc = auc
            delta = auc - base_auc
            print(f"{name:<28} {auc:>10.4f} {acc:>10.4f}"
                  + (f"   (delta {delta:+.4f})" if name != "baseline (5 features)" else ""))
            resultado[name] = {"auc": round(auc, 4), "acuracia": round(acc, 4), "delta_auc": round(delta, 4)}
        artefato["resultado"] = resultado

    with open(ARTEFATO, "w", encoding="utf-8") as f:
        json.dump(artefato, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nartefato gravado: {ARTEFATO}")


if __name__ == "__main__":
    main()
