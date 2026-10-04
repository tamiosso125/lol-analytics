"""Mede a taxa de vitória do time azul por corte temporal, no estado de empate.

POR QUE ESTE SCRIPT EXISTE: a Seção 5.3 do TCC afirma que o viés de lado é mais
forte aos 15 min, com base na taxa do conjunto de treino antigo. Depois do
retraining sobre 39.426 partidas a base mudou, e a bateria
(`tests/validate_predictions.py`) passou a acusar o corte de 25 min como o mais
favorável ao vermelho. Ou o texto envelheceu, ou o número estava errado. Este
script mede os dois e decide — não a memória.

Duas grandezas, deliberadamente distintas:
  1. TAXA BRUTA: entre partidas genuinamente empatadas no corte
     (|diferença de ouro| < 500), qual a taxa de vitória do azul? Não passa
     por modelo nenhum — é o dado.
  2. TAXA-BASE DO MODELO: a probabilidade que cada modelo atribui a um estado
     vazio, que é a sua taxa-base aprendida. Passa pelo modelo.

Uso:
    .venv\\Scripts\\python.exe docs\\taxa_base_por_corte.py
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import joblib

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "features_phases.csv"
SHARDS = RAIZ / "data" / "models_phases.joblib"
LIMITE_OURO = 500  # mesma definicao de "empate" usada na Secao 5.3


def brutos() -> dict[int, tuple[int, int, float]]:
    """Taxa de vitória do azul entre partidas empatadas, por corte.

    `features_phases.csv` está em formato LONGO: uma linha por
    (partida, corte), com `cutoff_min` como coluna — não como sufixo do
    nome das features. Procurar `gold_diff_15` não encontra nada, e o dicionário
    sai vazio em silêncio, que é a pior forma de falhar.
    """
    acc: dict[int, list[int]] = {}  # corte -> [azul venceu, empates]
    with CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                corte = int(row["cutoff_min"])
                g = int(float(row["gold_diff"]))
                w = int(float(row["blue_win"]))
            except (KeyError, ValueError):
                continue
            if abs(g) >= LIMITE_OURO:
                continue  # partida NAO empatada neste corte
            v = acc.setdefault(corte, [0, 0])
            v[0] += w
            v[1] += 1
    return {
        c: (v[0], v[1], v[0] / v[1]) if v[1] else (0, 0, float("nan"))
        for c, v in sorted(acc.items())
    }


def taxa_base_modelos() -> dict[int, float]:
    """Probabilidade que cada modelo da shards atribui a um estado vazio.

    `models_phases.joblib` guarda os quatro cortes. Um estado vazio `{}` faz o
    modelo cair no seu valor base aprendido — que é exatamente o número que a
    Seção 5.3 do TCC reporta.

    O XGBoost recusa dict (`Not supported type for data.<class 'dict'>`), então
    o estado é montado como DataFrame com as 5 features zeradas — que é a
    definição de "tudo empatado", não um atalho. Mesma construção de
    `tests/validate_predictions.py`.
    """
    import pandas as pd  # noqa: PLC0415

    features = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
    vazio = pd.DataFrame([[0] * len(features)], columns=features)
    modelos = joblib.load(os.fspath(SHARDS))
    return {c: float(m.predict_proba(vazio)[0, 1]) for c, m in modelos.items()}


def main() -> None:
    print("=" * 74)
    print("TAXA BRUTA entre partidas empatadas (|dif. de ouro| < 500)")
    print("=" * 74)
    print(f"{'corte':>7} {'azul vence':>12} {'empates':>9} {'taxa':>8}")
    b = brutos()
    for corte, (venc, n, taxa) in b.items():
        print(f"{corte:>5}min {venc:>12} {n:>9} {taxa:>8.4f}")
    pico_bruto = min(b, key=lambda c: b[c][2]) if b else None

    print()
    print("=" * 74)
    print("TAXA-BASE DO MODELO (estado vazio)")
    print("=" * 74)
    print(f"{'corte':>7} {'prob. azul':>12}")
    m = taxa_base_modelos()
    for corte in sorted(m):
        print(f"{corte:>5}min {m[corte]:>12.4f}")
    pico_mod = min(m, key=lambda c: m[c]) if m else None

    print()
    print("=" * 74)
    print("VEREDITO")
    print("=" * 74)
    print(f"  pico bruto : {pico_bruto}min")
    print(f"  pico modelo: {pico_mod}min")
    print("  -> coincidem" if pico_bruto == pico_mod
          else "  -> DIVERGEM: o texto da Secao 5.3 precisa ser corrigido")
    destino = RAIZ / "reports" / "taxa_base_por_corte.json"
    destino.write_text(
        json.dumps(
            {
                "bruto": {str(k): v for k, v in b.items()},
                "modelo": {str(k): v for k, v in m.items()},
                "pico_bruto": pico_bruto,
                "pico_modelo": pico_mod,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"  gravado: {destino}")


if __name__ == "__main__":
    main()