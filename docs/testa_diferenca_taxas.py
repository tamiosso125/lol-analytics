"""Testa se as taxas de vitória por corte diferem de verdade, ou se é ruído.

POR QUE: a Seção 5.3 do TCC afirmava que o viés de lado é "mais forte no meio
de jogo" e "enfraquece ao longo da partida". A medição na base de 39.426
partidas mostrou taxas brutas de 46,4% / 47,9% / 46,7% / 47,1% — um spread de
1,4 ponto percentual, com n caindo de 7.349 para 1.430. Antes de trocar um
achado por outro, é obrigatório perguntar se a diferença que se está
descrevendo existe.

Método: intervalo de Wilson para cada taxa (robusto a proporções extremas e a
n assimétrico) e teste de diferença de duas proporções para os pares
consecutivos. São testes exploratórios de múltiplas comparações — por isso o
ajuste de Holm, que corrige a multiplicidade.

Uso:
    .venv\\Scripts\\python.exe docs\\testa_diferenca_taxas.py
"""
from __future__ import annotations

import math
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LIMITE_OURO = 500


def wilson(vencedoras: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de Wilson de 95% para uma proporção."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = vencedoras / n
    denom = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / denom
    margem = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (centro - margem, centro + margem)


def dif_duas_proporcoes(a: tuple[int, int], b: tuple[int, int]) -> tuple[float, float]:
    """Diferença p_a - p_b e valor-p (teste de duas proporções, z)."""
    x1, n1 = a
    x2, n2 = b
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return (p1 - p2, 1.0)
    z = (p1 - p2) / se
    # p-valor bilateral da normal padrão
    p_val = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return (p1 - p2, p_val)


def holm(p_valores: list[float]) -> list[float]:
    """Ajuste de Holm para múltiplas comparações. Retorna p ajustados."""
    m = len(p_valores)
    ordem = sorted(range(m), key=lambda i: p_valores[i])
    ajustados = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(ordem):
        adj = min(1.0, (m - rank) * p_valores[idx])
        running = max(running, adj)  # exige monotonicidade
        ajustados[idx] = running
    return ajustados


def main() -> None:
    import json

    dados = json.loads(
        (RAIZ / "reports" / "taxa_base_por_corte.json").read_text(encoding="utf-8")
    )["bruto"]

    print("=" * 76)
    print(f"TAXA DE VITÓRIA DO AZUL ENTRE PARTIDAS EMPATADAS (|ouro| < {LIMITE_OURO})")
    print("=" * 76)
    print(f"{'corte':>7} {'taxa':>8} {'IC 95% (Wilson)':>24} {'n':>8}")
    cortes = sorted(dados, key=int)
    for c in cortes:
        venc, n, taxa = dados[c]
        lo, hi = wilson(venc, n)
        print(f"{int(c):>5}min {taxa:>8.4f}   [{lo:.4f}, {hi:.4f}]  {n:>8}")

    print()
    print("=" * 76)
    print("TODOS OS PARES (ajuste de Holm para 6 comparações)")
    print("=" * 76)
    pares, pv = [], []
    for a, b in combinations(cortes, 2):
        dif, p = dif_duas_proporcoes(
            (dados[a][0], dados[a][1]), (dados[b][0], dados[b][1])
        )
        pares.append((a, b, dif, p))
        pv.append(p)
    for (a, b, dif, p), pa in zip(pares, holm(pv)):
        marca = "diferente" if pa < 0.05 else "iguais (ruído)"
        print(f"  {int(a):>2}min vs {int(b):>2}min  dif {dif*100:+.2f} pp  "
              f"p={p:.3f}  p_holm={pa:.3f}  -> {marca}")

    print()
    if all(pa >= 0.05 for pa in holm(pv)):
        print("VEREDITO: nenhuma diferença sobrevive ao ajuste. As quatro taxas")
        print("são estatisticamente INDISTINGUEIS: o viés de lado é CONSTANTE")
        print("ao longo da partida, e não há pico no meio de jogo.")
    else:
        print("VEREDITO: ao menos um par difere apos o ajuste (ver tabela).")


if __name__ == "__main__":
    main()