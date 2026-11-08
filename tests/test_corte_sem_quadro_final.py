r"""O estado no corte nunca pode ser o quadro final de uma partida já encerrada.

Invariante 1 do AGENTS.md. A timeline da Riot termina com um quadro extra no
instante do fim do jogo; numa partida de 24:16, `frames[25]` é esse quadro, e
até 2026-11-08 ele entrava como "estado aos 25 minutos" (2.642 partidas aos 25,
AUC-ROC de 1,0 nelas). Este teste confere, nas partidas reais do banco, que
nenhuma partida mais curta que o corte gera variáveis naquele corte, e, num
caso sintético, que o quadro final é recusado.

Uso:  .venv\Scripts\python.exe tests\test_corte_sem_quadro_final.py
Precisa do banco.
"""
import sys

sys.path.insert(0, ".")

from src.db import get_conn  # noqa: E402
from src.features.build_features import CUTOFFS, corte_disponivel, features_from_timeline  # noqa: E402


def main() -> int:
    falhas = 0
    # sintético: 25 quadros de minuto (0..24) + quadro final -> não há estado aos 25
    quadros = [{"timestamp": i * 60_000, "participantFrames": {}, "events": []} for i in range(25)]
    quadros.append({"timestamp": 24 * 60_000 + 16_000, "participantFrames": {}, "events": []})
    if corte_disponivel(quadros, 25) or features_from_timeline({"info": {"frames": quadros}}, 25) is not None:
        print("FALHA: quadro final aceito como estado aos 25 minutos")
        falhas += 1
    if not corte_disponivel(quadros, 24):
        print("FALHA: o quadro de minuto 24 (jogo em andamento) foi recusado")
        falhas += 1

    conn = get_conn()
    cur = conn.cursor()
    # as partidas mais curtas que cada corte, mais um lote de controle
    cur.execute("""SELECT t.payload, m.game_duration_s FROM raw_timelines t
                   JOIN matches m ON m.match_id = t.match_id
                   WHERE m.game_duration_s < 1500 ORDER BY m.game_duration_s DESC LIMIT 400""")
    testadas = 0
    for payload, dur in cur:
        for c in CUTOFFS:
            if dur < c * 60:
                testadas += 1
                if features_from_timeline(payload, c) is not None:
                    falhas += 1
                    print(f"FALHA: partida de {dur}s com variáveis aos {c} min")
    conn.close()
    print(f"{testadas} (partida, corte) com partida mais curta que o corte; {falhas} falha(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
