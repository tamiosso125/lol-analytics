"""Teste de fumaça SEM banco e SEM API: valida o pipeline
features -> modelos com dados sintéticos.

Gera partidas artificiais (vantagem de ouro correlacionada à vitória),
constrói o CSV de features e roda o baseline. Serve para confirmar que
o ambiente está funcional antes da coleta real.

Uso:  python tests/smoke_test.py
"""
import os
import sys
import tempfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.features.build_features import features_from_timeline

rng = np.random.default_rng(42)


def fake_timeline(blue_advantage: float) -> dict:
    """Timeline mínima compatível com features_from_timeline."""
    frames = []
    for minute in range(20):
        pframes = {}
        for pid in range(1, 11):
            team_bonus = blue_advantage if pid <= 5 else -blue_advantage
            pframes[str(pid)] = {
                "totalGold": int(500 + minute * (350 + team_bonus * 40) + rng.normal(0, 80)),
                "xp": int(600 + minute * (400 + team_bonus * 30) + rng.normal(0, 100)),
            }
        events = []
        if rng.random() < 0.4:
            killer_blue = rng.random() < (0.5 + blue_advantage * 0.12)
            events.append(
                {"type": "CHAMPION_KILL", "killerId": int(rng.integers(1, 6)) if killer_blue else int(rng.integers(6, 11))}
            )
        frames.append({"participantFrames": pframes, "events": events})
    return {"info": {"frames": frames}}


def main() -> None:
    rows = []
    for i in range(400):
        adv = rng.normal(0, 1)
        feats = features_from_timeline(fake_timeline(adv))
        assert feats is not None
        feats["match_id"] = f"FAKE_{i}"
        feats["blue_win"] = int(adv + rng.normal(0, 0.6) > 0)
        rows.append(feats)

    # roda dentro de um diretório temporário: o CSV sintético NÃO pode
    # sobrescrever o data/features.csv real — a API (/stats/gold15) lê
    # esse arquivo e passaria a exibir dados falsos no dashboard
    old_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            os.chdir(tmp)
            df = pd.DataFrame(rows)
            os.makedirs("data", exist_ok=True)
            df.to_csv("data/features.csv", index=False)
            print(f"[1/2] {len(df)} partidas sintéticas -> {tmp}/data/features.csv")

            from src.models import train_baseline

            print("[2/2] Rodando baseline nos dados sintéticos:")
            train_baseline.main()
        finally:
            # sai do tempdir antes da limpeza (Windows não remove o cwd)
            os.chdir(old_cwd)
    print("\nSmoke test concluído — pipeline funcional.")


if __name__ == "__main__":
    main()
