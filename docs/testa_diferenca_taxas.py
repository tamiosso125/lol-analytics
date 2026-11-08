"""Testa se as taxas de vitória do azul entre partidas empatadas diferem entre cortes.

POR QUE: a Seção 5.3 compara a taxa de vitória do azul entre partidas com
diferença de ouro menor que 500 nos cortes de 10, 15, 20 e 25 minutos.

2026-11-08 (parecer do orientador): a versão anterior usava o teste z de duas
proporções com variância combinada, que supõe grupos INDEPENDENTES. Os grupos
não são: a mesma partida pode estar empatada em mais de um corte (aqui se
mede quantas). O teste passou a usar a PARTIDA como unidade: reamostragem
(bootstrap) das partidas empatadas em algum corte, com reposição; em cada
reamostra, a taxa de cada corte é recalculada sobre as partidas sorteadas que
estão empatadas naquele corte. A dependência entre cortes fica preservada,
porque a partida entra ou sai inteira. Intervalo de 95% por percentis e
valor-p bilateral pela reamostra centrada; ajuste de Holm para os seis pares.

Uso:
    .venv\\Scripts\\python.exe docs\\testa_diferenca_taxas.py

Grava:
    reports/vies_cortes_por_partida.json
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parent.parent
LIMITE_OURO = 500
CORTES = [10, 15, 20, 25]
B = 2000
SEMENTE = 42


def wilson(vencedoras: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de Wilson de 95% para uma proporção."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = vencedoras / n
    denom = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / denom
    margem = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (centro - margem, centro + margem)


def holm(p_valores: list[float]) -> list[float]:
    """Ajuste de Holm para múltiplas comparações. Retorna p ajustados."""
    m = len(p_valores)
    ordem = sorted(range(m), key=lambda i: p_valores[i])
    ajustados = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(ordem):
        running = max(running, min(1.0, (m - rank) * p_valores[idx]))  # exige monotonicidade
        ajustados[idx] = running
    return ajustados


def main() -> None:
    df = pd.read_csv(RAIZ / "data" / "features_phases.csv")
    emp = df[df["gold_diff"].abs() < LIMITE_OURO]
    # uma linha por partida, uma coluna por corte (NaN = não empatada naquele corte)
    tab = emp.pivot_table(index="match_id", columns="cutoff_min", values="blue_win", aggfunc="first")[CORTES]
    arr = tab.to_numpy(dtype=float)
    em_quantos = (~np.isnan(arr)).sum(axis=1)

    print("=" * 76)
    print(f"VITÓRIA DO AZUL ENTRE PARTIDAS EMPATADAS (|ouro| < {LIMITE_OURO}), PARTIDA COMO UNIDADE")
    print("=" * 76)
    taxas = {}
    for i, c in enumerate(CORTES):
        col = arr[:, i][~np.isnan(arr[:, i])]
        k, n = int(col.sum()), int(len(col))
        lo, hi = wilson(k, n)
        taxas[c] = {"vitorias_azul": k, "partidas": n, "taxa": round(k / n, 4), "ic95_wilson": [round(lo, 4), round(hi, 4)]}
        print(f"{c:>5} min  taxa {k / n:.4f}  [{lo:.4f}, {hi:.4f}]  n {n}")
    print(f"\npartidas empatadas distintas: {len(tab)} | linhas partida x corte: {len(emp)}")
    dist = {int(k): int(v) for k, v in pd.Series(em_quantos).value_counts().sort_index().items()}
    print(f"em quantos cortes cada uma aparece: {dist}")
    sobreposicao = {}
    for a, b in combinations(CORTES, 2):
        ia, ib = CORTES.index(a), CORTES.index(b)
        ambas = int((~np.isnan(arr[:, ia]) & ~np.isnan(arr[:, ib])).sum())
        menor = min(taxas[a]["partidas"], taxas[b]["partidas"])
        sobreposicao[f"{a}x{b}"] = {"em_comum": ambas, "pct_do_menor": round(100 * ambas / menor, 1)}

    rng = np.random.default_rng(SEMENTE)
    boot = np.empty((B, len(CORTES)))
    for r in range(B):
        boot[r] = np.nanmean(arr[rng.integers(0, len(arr), len(arr))], axis=0)

    pares, pv = [], []
    for a, b in combinations(CORTES, 2):
        ia, ib = CORTES.index(a), CORTES.index(b)
        d0 = float(np.nanmean(arr[:, ia]) - np.nanmean(arr[:, ib]))
        dif = boot[:, ia] - boot[:, ib]
        p = float((np.abs(dif - d0) >= abs(d0)).mean())
        pares.append({"par": f"{a}x{b}", "diferenca_pp": round(100 * d0, 2),
                      "ic95_pp": [round(100 * float(np.percentile(dif, 2.5)), 2),
                                  round(100 * float(np.percentile(dif, 97.5)), 2)],
                      "p": round(p, 3), **sobreposicao[f"{a}x{b}"]})
        pv.append(p)
    for par, pa in zip(pares, holm(pv)):
        par["p_holm"] = round(pa, 3)
        print(f"  {par['par']:>6}: dif {par['diferenca_pp']:+.2f} pp  IC95 [{par['ic95_pp'][0]:+.2f}, "
              f"{par['ic95_pp'][1]:+.2f}]  p={par['p']:.3f}  p_holm={pa:.3f}  "
              f"({par['em_comum']} partidas em comum, {par['pct_do_menor']}% do menor grupo)")
    menor_holm = min(p["p_holm"] for p in pares)
    print(f"\nmenor p ajustado por Holm: {menor_holm:.3f}")
    print("nenhuma diferença detectada" if menor_holm >= 0.05 else "ao menos um par difere")

    destino = RAIZ / "reports" / "vies_cortes_por_partida.json"
    destino.write_text(json.dumps({
        "medido_em": date.today().isoformat(),
        "metodo": f"bootstrap por partida, {B} reamostragens, semente {SEMENTE}; IC por percentis; "
                  "p bilateral pela reamostra centrada; Holm para 6 pares",
        "limite_ouro": LIMITE_OURO, "partidas_empatadas_distintas": int(len(tab)),
        "linhas_partida_corte": int(len(emp)), "partidas_por_numero_de_cortes": dist,
        "taxas": {str(c): v for c, v in taxas.items()}, "pares": pares, "menor_p_holm": menor_holm,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"gravado: {destino}")


if __name__ == "__main__":
    main()
