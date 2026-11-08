"""Garante que as variáveis de `build_features_antigos` não usam nada depois do corte.

Invariante 1 do AGENTS.md: cortar a timeline em `frames[: cutoff + 1]` não
pode mudar nenhuma variável. Se mudar, a variável olha para o futuro.

Uso:  .venv\\Scripts\\python.exe tests\\test_features_antigos_sem_vazamento.py
Precisa do banco (usa 200 timelines reais).
"""
import copy
import sys

sys.path.insert(0, ".")

from src.db import get_conn  # noqa: E402
from src.features.build_features import CUTOFFS  # noqa: E402
from src.features.build_features_antigos import antigos_features, itens_finalizados  # noqa: E402


def main() -> int:
    item_gold = itens_finalizados()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT payload FROM raw_timelines LIMIT 200")
    falhas = 0
    testadas = 0
    for (payload,) in cur:
        for cutoff in CUTOFFS:
            cheio = antigos_features(payload, cutoff, item_gold)
            if cheio is None:
                continue
            cortado = copy.deepcopy(payload)
            # depois do corte fica só um quadro VAZIO: marca que o jogo seguiu
            # (corte_disponivel exige um quadro posterior, 2026-11-08) sem
            # carregar nenhum dado do futuro
            cortado["info"]["frames"] = cortado["info"]["frames"][: cutoff + 1] + [{}]
            igual = antigos_features(cortado, cutoff, item_gold)
            testadas += 1
            if cheio != igual:
                falhas += 1
                dif = [k for k in cheio if cheio[k] != igual.get(k)]
                print(f"VAZAMENTO no corte {cutoff}: {dif}")
    print(f"{testadas} (partida, corte) testados, {falhas} com vazamento")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
