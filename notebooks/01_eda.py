"""Análise exploratória inicial (seção 4.5 do TCC).

Roda como script ou converte para notebook. Requer partidas no banco.
Uso:  python notebooks/01_eda.py
"""
import pandas as pd

from src.db import get_conn

conn = get_conn()

matches = pd.read_sql("SELECT * FROM matches", conn)
participants = pd.read_sql("SELECT * FROM participants", conn)
conn.close()

print(f"Partidas: {len(matches)} | Participantes: {len(participants)}")
print("\nDuração (min):")
print((matches["game_duration_s"] / 60).describe().round(1))

print("\nTop 15 campeões mais jogados:")
print(participants["champion_name"].value_counts().head(15))

print("\nWin rate por posição (sanidade — deve ficar ~0.50):")
print(participants.groupby("team_position")["win"].mean().round(3))

print("\nKDA médio por posição:")
participants["kda"] = (participants["kills"] + participants["assists"]) / (
    participants["deaths"].clip(lower=1)
)
print(participants.groupby("team_position")["kda"].mean().round(2))
