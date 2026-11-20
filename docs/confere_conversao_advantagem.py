"""Confere os números de conversão de vantagem material citados na Seção 5.3.

POR QUE: o TCC afirma "com vantagem de +2.000 a +4.000 aos 15 min, o azul
venceu 84,0% no profissional contra ~68% no solo queue" e "+4.000 a +6.000,
~95% contra ~81%". Esses números foram medidos sobre a base antiga. A coleta
triplicou a base e o retreino foi refeito — a única checagem honesta é remedir.
O lado profissional (Oracle's Elixir) não mudou e é conferido no mesmo script
para que a comparação continue sendo feita sobre a mesma definição de faixa.

CORREÇÃO (2026-11-17): até esta data o lado profissional lia a PRIMEIRA linha
do lado Blue de cada jogo. No CSV do Oracle's Elixir cada jogo tem 12 linhas
(10 de jogador e 2 de time, estas com position == "team"), e a primeira linha
Blue é a do jogador do TOPO (88.474 dos 88.593 jogos). `golddiffat15` nessa
linha é a vantagem de ouro do topo contra o topo adversário, não a do time, e
o solo queue usa a diferença de ouro do TIME. Resultado errado nas duas faixas
(81,5%, n = 3.294; e 91,7%, n = 72). Agora usa a linha do time, que é também o
que a tela Competitivo e a API (`/stats/pro/gold15`, tabela pro_games) usam.

Uso:
    .venv\\Scripts\\python.exe docs\\confere_conversao_advantagem.py
"""
from __future__ import annotations

import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "features_phases.csv"

# (nome citado no TCC, corte_min, faixa de ouro do time azul)
FAIXAS = [
    ("+2.000 a +4.000", 15, 2000, 4000),
    ("+4.000 a +6.000", 15, 4000, 6000),
]


def solo_queue() -> dict[str, tuple[int, int]]:
    print("=" * 74)
    print("SOLO QUEUE (data/features_phases.csv, dados brutos)")
    print("=" * 74)
    print(f"{'faixa':>16} {'corte':>6} {'vitorias':>9} {'n':>7} {'taxa azul':>11}")
    acc: dict[str, tuple[int, int]] = {}
    for nome, corte, lo, hi in FAIXAS:
        venc, n = 0, 0
        with CSV.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    if int(row["cutoff_min"]) != corte:
                        continue
                    g = int(float(row["gold_diff"]))
                    if not (lo <= g < hi):
                        continue
                    venc += int(float(row["blue_win"]))
                    n += 1
                except (KeyError, ValueError):
                    continue
        taxa = venc / n if n else float("nan")
        print(f"{nome:>16} {corte:>5}min {venc:>9} {n:>7} {taxa:>11.4f}")
        acc[nome] = (venc, n)
    return acc


def profissional() -> None:
    print()
    print("=" * 74)
    print("PROFISSIONAL (Oracle's Elixir, data/pro)")
    print("=" * 74)
    # A coluna de diferenca de ouro no Oracle's Elixir e `golddiffat<min>`,
    # nao `gold_diff`: sao 165 colunas e o nome segue o padrao
    # goldat15 / opp_goldat15 / golddiffat15. Procurar "gold_diff" nao acha.
    alvos = {"golddiffat15": 15}
    acc = {nome: [0, 0] for nome, _c, _lo, _hi in FAIXAS}  # -> [vitorias, n]
    jogos = 0
    vistos: set[str] = set()  # gameid ja contabilizado
    lados: dict[str, int] = {}
    for a in sorted((RAIZ / "data" / "pro").glob("*.csv")):
        with a.open(encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                lado = str(row.get("side", "")).strip()
                lados[lado] = lados.get(lado, 0) + 1
                if lado.lower() != "blue":
                    continue
                # Linha do TIME, nao a de jogador: a de jogador traz a vantagem
                # de ouro daquele jogador contra o oponente da mesma funcao.
                if str(row.get("position", "")).strip().lower() != "team":
                    continue
                gid = str(row.get("gameid", "")).strip()
                if not gid or gid in vistos:
                    continue  # 1 linha de time BLUE por jogo: conta uma so
                try:
                    g = int(float(row["golddiffat15"]))
                except (KeyError, ValueError, TypeError):
                    continue
                vistos.add(gid)
                jogos += 1
                try:
                    venceu = int(float(row["result"])) == 1
                except (KeyError, ValueError, TypeError):
                    continue
                for nome, _c, lo, hi in FAIXAS:
                    if lo <= g < hi:
                        acc[nome][0] += venceu
                        acc[nome][1] += 1
    print(f"  valores de 'side' vistos: {lados}")
    print(f"  jogos (linha do time azul) com golddiffat15: {jogos}")
    print(f"\n{'faixa':>16} {'vitorias':>9} {'n':>8} {'taxa azul':>11}")
    for nome, _c, _lo, _hi in FAIXAS:
        venc, n = acc[nome]
        taxa = venc / n if n else float("nan")
        print(f"{nome:>16} {venc:>9} {n:>8} {taxa:>11.4f}")
    return {nome: (acc[nome][0], acc[nome][1])
            for nome, _c, _lo, _hi in FAIXAS}


def diferenca_significativa(
    a: tuple[int, int], b: tuple[int, int]
) -> tuple[float, float]:
    """Diferenca p_a - p_b e o z de duas proporcoes independentes."""
    import math

    x1, n1 = a
    x2, n2 = b
    if not n1 or not n2:
        return (float("nan"), float("nan"))
    p1, p2 = x1 / n1, x2 / n2
    pool = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pool * (1 - pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return (p1 - p2, float("nan"))
    return (p1 - p2, (p1 - p2) / se)


if __name__ == "__main__":
    solo = solo_queue()
    prof = profissional()
    print()
    print("=" * 74)
    print("DIFERENÇA ENTRE OS CENÁRIOS (mesma faixa de vantagem)")
    print("=" * 74)
    print(f"{'faixa':>16} {'prof':>8} {'solo':>8} {'dif (pp)':>9} {'z':>7}")
    for nome, _c, _lo, _hi in FAIXAS:
        pv, np_ = prof[nome]
        sv, ns = solo[nome]
        dif, z = diferenca_significativa((pv, np_), (sv, ns))
        aviso = "  <- n profissional pequeno, indicativa" if np_ < 100 else ""
        print(f"{nome:>16} {pv/np_:>8.4f} {sv/ns:>8.4f} {dif*100:>9.2f} "
              f"{z:>7.2f}{aviso}")
    print()
    pequenas = [nome for nome, _c, _lo, _hi in FAIXAS if prof[nome][1] < 100]
    if pequenas:
        print("Faixas indicativas por n profissional pequeno: " + ", ".join(pequenas))
    else:
        print("As duas faixas têm n profissional suficiente (>= 100).")