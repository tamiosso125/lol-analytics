"""Remede o teste (ii) de robustez: taxa de vitória por faixa de duração.

POR QUE ESTE SCRIPT: o teste (ii) da Seção 4.5/5.3 sustenta que a
assimetria por lado não é confundida com "partidas longas são um tipo
diferente de jogo". O número que o texto citava — "44%-47%" — é de
2026-07-08, medido sobre 23.133 partidas. A base hoje é 41.063, quase o
dobro, e a região NA1 foi de 1.446 para 7.159. Um teste de robustez citado
sem data e sem base é um teste que ninguém pode reproduzir.

O número que este script imprime mudou com a base, e o TCC teve de mudar
junto: a rodada final da KR levou a amplitude de 1,6 para 1,7 pp e deslocou o
máximo da faixa 25-30 de 47,2% para 47,3%. A checagem 17 de
`docs/verifica_tcc.py` amarra o que o texto cita à soma das contagens deste
JSON, justamente para essa troca não voltar a passar em silêncio.

O que mede: taxa de vitória do time AZUL, **incondicional** (sem filtro de
empate), por faixa de duração total da partida — a definição que o diário
registrou em 2026-07-08. Responde se o viés depende de a partida ser longa,
e não de o jogo estar empatado naquele minuto.

Uso:
    .venv\\Scripts\\python.exe docs\\testa_faixa_duracao.py

Grava:
    reports/faixa_duracao.json

DUAS ARMADILHAS JÁ COMETIDAS NESTE SCRIPT, ambas registradas no código:

1. Chavear o dicionário de ordem pelos MINUTOS (inteiros) e comparar com o
   rótulo que o `CASE` devolve (string). Todas as linhas eram descartadas e
   a tabela saía sem nenhum número — resultado vazio com aparência de "não
   há partidas nestas faixas", que é bem diferente de "o comando está
   errado".

2. Agregar sobre `participants` sem agregar antes. `win` é por JOGADOR (cinco
   por partida), então a média de uma coluna que conta cinco por partida
   retorna 50,0% por simetria — número plausível e errado. O certo é
   reduzir a uma linha por partida e testar se o time azul venceu.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db import get_conn  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent

# (rótulo, minuto inicial, minuto final). O rótulo precisa bater com o que o
# CASE do SQL devolve.
FAIXAS = [("0-25", 0, 25), ("25-30", 25, 30), ("30-35", 30, 35),
          ("35-40", 35, 40), ("40+", 40, 100)]

SQL = """
SELECT faixa, COUNT(*) AS jogos,
       ROUND(100.0 * AVG(CASE WHEN v_blue > 0 THEN 1 ELSE 0 END)::numeric, 1)
         AS pct_azul
FROM (
  SELECT m.match_id,
         CASE
           WHEN m.game_duration_s < 1500 THEN '0-25'
           WHEN m.game_duration_s < 1800 THEN '25-30'
           WHEN m.game_duration_s < 2100 THEN '30-35'
           WHEN m.game_duration_s < 2400 THEN '35-40'
           ELSE '40+'
         END AS faixa,
         SUM(CASE WHEN p.team_id = 100 AND p.win THEN 1 ELSE 0 END) AS v_blue
  FROM matches m
  JOIN participants p ON p.match_id = m.match_id
  WHERE m.queue_id = 420
  GROUP BY m.match_id
) t
GROUP BY 1
"""


def main() -> None:
    cur = get_conn().cursor()
    cur.execute(SQL)
    por_rotulo = {rot: (lo, hi) for rot, lo, hi in FAIXAS}
    # desempacota por rotulo: (faixa, partidas, pct_azul) + (lo, hi) da FAIXAS
    dados = []
    for rot, n, p in cur.fetchall():
        if rot not in por_rotulo:
            continue
        lo, hi = por_rotulo[rot]
        dados.append({"faixa": rot, "min": lo,
                      "max": (hi if hi < 100 else None),
                      "jogos": int(n), "pct_azul": float(p)})
    dados.sort(key=lambda d: d["min"])

    print("=" * 68)
    print("TAXA DE VITORIA DO AZUL, INCONDICIONAL, POR FAIXA DE DURACAO")
    print("=" * 68)
    print(f"{'faixa (min)':<16}{'partidas':>11}{'azul':>9}")
    for d in dados:
        rot = f"{d['min']}-{d['max']}" if d["max"] else f"{d['min']}+"
        print(f"{rot:<16}{d['jogos']:>11}{d['pct_azul']:>9.1f}")

    if not dados:
        raise SystemExit(
            "nenhuma faixa devolvida — o SQL mudou ou nao ha partidas na fila 420"
        )

    taxas = [d["pct_azul"] for d in dados]
    amplitude = max(taxas) - min(taxas)
    todos_abaixo = all(t < 50 for t in taxas)
    estreito = amplitude <= 5

    print()
    print(f"minimo   : {min(taxas):.1f}%")
    print(f"maximo   : {max(taxas):.1f}%")
    print(f"amplitude: {amplitude:.1f} pp")
    print(f"todas abaixo de 50%? {todos_abaixo}")
    print(f"amplitude <= 5 pp?   {estreito}")
    print()
    if todos_abaixo and estreito:
        print("VEREDITO: a taxa e plana e fica abaixo de 50% em toda a faixa de")
        print("          duracao — o vies NAO e confundido com partida longa.")
    else:
        print("VEREDITO: o teste (ii) NAO se sustenta no estado atual. Alguma")
        print("          faixa cruzou 50%, ou a amplitude passou de 5 pp. O texto")
        print("          precisa ser reescrito antes de afirmar este teste.")

    destino = RAIZ / "reports" / "faixa_duracao.json"
    destino.write_text(
        json.dumps({
            "medido_em": date.today().isoformat(),
            "definicao": "taxa de vitória do time azul, incondicional, por "
                         "faixa de duração total da partida",
            "faixas": dados,
            "amplitude_pp": round(amplitude, 1),
            "todos_abaixo_de_50": todos_abaixo,
            "amplitude_ate_5pp": estreito,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"gravado: {destino}")


if __name__ == "__main__":
    main()