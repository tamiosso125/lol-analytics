"""Dashboard da plataforma (objetivo específico f do TCC).

Uso:  streamlit run src/dashboard/app.py
"""
import sys
from pathlib import Path

# streamlit run (diferente de `python -m`) não adiciona a raiz do projeto
# ao sys.path, então o import `from src...` abaixo falharia sem isto.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import get_conn

st.set_page_config(page_title="Hextech Lab", layout="wide")
st.title("Hextech Lab — Análise de Dados Competitivos")


@st.cache_data(ttl=300)
def load(sql: str, params=None) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql(sql, conn, params=params)


# ---------- KPIs ----------
kpi = load(
    """SELECT (SELECT COUNT(*) FROM matches) AS matches,
              (SELECT COUNT(DISTINCT puuid) FROM participants) AS players,
              (SELECT AVG(game_duration_s)/60.0 FROM matches) AS avg_min"""
)
c1, c2, c3 = st.columns(3)
c1.metric("Partidas", int(kpi.matches[0]))
c2.metric("Jogadores únicos", int(kpi.players[0]))
c3.metric("Duração média (min)", f"{kpi.avg_min[0]:.1f}" if kpi.avg_min[0] else "—")

# ---------- Campeões ----------
st.header("Campeões")
min_games = st.slider("Mínimo de jogos", 10, 200, 30, step=10)
champs = load(
    """SELECT champion_name, COUNT(*) AS jogos, AVG(win::int) AS win_rate
       FROM participants GROUP BY champion_name
       HAVING COUNT(*) >= %(mg)s ORDER BY win_rate DESC""",
    {"mg": min_games},
)
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Maior win rate")
    fig = px.bar(champs.head(15), x="win_rate", y="champion_name", orientation="h")
    fig.add_vline(x=0.5, line_dash="dash")
    st.plotly_chart(fig, use_container_width=True)
with col_b:
    st.subheader("Mais jogados")
    top = champs.sort_values("jogos", ascending=False).head(15)
    st.plotly_chart(
        px.bar(top, x="jogos", y="champion_name", orientation="h"),
        use_container_width=True,
    )

# ---------- Objetivos x vitória ----------
st.header("Objetivos e vitória")
obj = load(
    """SELECT win, AVG(dragons) AS dragons, AVG(barons) AS barons,
              AVG(towers) AS towers, AVG(heralds) AS heralds
       FROM teams GROUP BY win"""
)
obj_m = obj.melt(id_vars="win", var_name="objetivo", value_name="media")
st.plotly_chart(
    px.bar(obj_m, x="objetivo", y="media", color="win", barmode="group"),
    use_container_width=True,
)

# ---------- Consulta em linguagem natural ----------
st.header("Pergunte aos dados (linguagem natural)")
question = st.text_input("Ex.: qual posição tem o maior KDA médio?")
if question:
    try:
        from src.nlq.nl_to_sql import ask

        result = ask(question)
        st.code(result["sql"], language="sql")
        st.dataframe(pd.DataFrame(result["rows"], columns=result["columns"]))
    except Exception as exc:
        st.error(f"Não foi possível responder: {exc}")
