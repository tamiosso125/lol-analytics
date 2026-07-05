"""Interface em linguagem natural (objetivo específico g do TCC).

Abordagem: text-to-SQL — o LLM recebe o schema e a pergunta do usuário
e gera uma query SELECT, que é validada antes da execução.

Camadas de segurança:
  1. apenas um statement, começando com SELECT (sem ; encadeado);
  2. palavras-chave de escrita bloqueadas;
  3. somente tabelas do schema são permitidas;
  4. statement_timeout no PostgreSQL.

Requer ANTHROPIC_API_KEY no ambiente (.env).

Uso:  python -m src.nlq.nl_to_sql "qual campeão tem maior win rate?"
"""
import os
import re
import sys

import anthropic
import psycopg2

from src.db import get_conn
from src.nlq.schema_context import SCHEMA_DESCRIPTION

ALLOWED_TABLES = {
    "matches", "teams", "participants", "players", "bans",
    "pro_games", "pro_players",
}
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy)\b",
    re.IGNORECASE,
)


class SqlExecutionError(Exception):
    """SQL gerada passou na validação de segurança mas falhou ao rodar no
    banco (coluna/tabela inexistente, erro de sintaxe etc.) — carrega a
    SQL e o erro original para diagnóstico (não é pra esconder do
    usuário, ele precisa disso para melhorar o prompt/schema)."""

    def __init__(self, sql: str, cause: Exception):
        self.sql = sql
        self.cause = cause
        super().__init__(str(cause))


def generate_sql(
    question: str,
    history: list[dict] | None = None,
    model: str = "claude-haiku-4-5-20251001",
) -> str:
    """history: turnos anteriores da mesma conversa, cada um
    {"question": ..., "sql": ...} — dá contexto para perguntas de
    acompanhamento ("agora filtre só os challenger")."""
    messages = []
    for turn in history or []:
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["sql"]})
    messages.append({"role": "user", "content": question})

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=model,
        # perguntas com várias condições (ex.: matchup com 5 campeões
        # específicos) geram SQL com vários EXISTS — 500 tokens cortava
        # a query no meio, causando erro de sintaxe em vez de rodar
        max_tokens=1200,
        temperature=0,  # determinístico — necessário para o benchmark de execution accuracy
        system=SCHEMA_DESCRIPTION,
        messages=messages,
    )
    if msg.stop_reason == "max_tokens":
        raise ValueError(
            "A pergunta é complexa demais — a consulta gerada foi cortada antes de "
            "terminar. Tente dividir em perguntas menores."
        )
    sql = msg.content[0].text.strip()
    return sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()


def _without_string_literals(sql: str) -> str:
    """Remove o conteúdo de literais de string ('...') antes das checagens
    estruturais abaixo — evita falso positivo de pontuação/palavras dentro
    de texto livre (ex.: um aviso gerado pelo LLM com ';' na frase)."""
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


def validate_sql(sql: str) -> None:
    if not sql.lower().lstrip().startswith("select"):
        raise ValueError("Apenas SELECT é permitido.")
    structural = _without_string_literals(sql)
    if ";" in structural.rstrip().rstrip(";"):
        raise ValueError("Múltiplos statements não são permitidos.")
    if FORBIDDEN.search(structural):
        raise ValueError("Query contém palavra-chave proibida.")
    tables = set(re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)", structural, re.IGNORECASE))
    unknown = {t.lower() for t in tables} - ALLOWED_TABLES
    if unknown:
        raise ValueError(f"Tabelas não permitidas: {unknown}")


def run_query(sql: str) -> tuple[list[str], list[tuple]]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SET statement_timeout = '10s'")
        cur.execute(sql)
        cols = [d.name for d in cur.description]
        return cols, cur.fetchall()


def ask(question: str, history: list[dict] | None = None) -> dict:
    sql = generate_sql(question, history)
    validate_sql(sql)
    try:
        cols, rows = run_query(sql)
    except psycopg2.Error as exc:
        raise SqlExecutionError(sql, exc) from exc
    return {"question": question, "sql": sql, "columns": cols, "rows": rows}


def explain_result(question: str, sql: str, columns: list[str], rows: list[tuple]) -> str:
    """Explicação em linguagem natural do resultado, para usuários sem SQL."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    preview = "\n".join(", ".join(str(v) for v in row) for row in rows[:10])
    prompt = (
        f"Pergunta do usuário: {question}\n\n"
        f"SQL executada:\n{sql}\n\n"
        f"Colunas do resultado: {', '.join(columns)}\n"
        f"Primeiras linhas do resultado:\n{preview or '(nenhuma linha)'}\n\n"
        "Convenções do banco — use para não errar a leitura dos números (não "
        "repita estas frases na resposta): team_id 100 é sempre o time AZUL e "
        "team_id 200 é sempre o time VERMELHO (nunca o contrário); nas tabelas "
        "de jogos PROFISSIONAIS (pro_games/pro_players), o lado já vem como "
        "texto 'Blue'/'Red'; colunas de win rate/taxa já vêm como fração entre "
        "0 e 1 (0.58 = 58%); estatísticas de participantes (kills, gold_earned "
        "etc.) e a duração da partida são totais FINAIS de fim de jogo, nunca "
        "um instante específico.\n\n"
        "Explique em português, em texto corrido simples (sem markdown — nada de "
        "#, ** ou listas) e sem jargão de SQL (não use termos como SELECT, GROUP "
        "BY, JOIN etc.), como chegamos nesse resultado a partir dos dados de "
        "partidas de League of Legends — o que foi contado ou calculado e o que "
        "os números significam (2-4 frases).\n\n"
        "Depois, avalie a confiança estatística: se alguma comparação se apoia em "
        "poucas partidas (menos de ~30 por grupo), diga explicitamente que a "
        "amostra é pequena demais para uma conclusão firme — com n=12, por "
        "exemplo, uma taxa de vitória pode variar dezenas de pontos percentuais "
        "só por acaso, então diferenças entre grupos pequenos podem ser ruído.\n\n"
        "Por fim, se você tiver conhecimento de jogo relevante que os números não "
        "capturam (sinergias conhecidas de composição, estilo dos campeões, fase "
        "do jogo em que cada um é forte), acrescente 1-2 frases começando "
        "exatamente com 'Leitura de jogo:' — deixando claro que isso vem do "
        "conhecimento do jogo, não destes dados, e apontando quando ele "
        "concorda ou discorda dos números. Se não tiver nada relevante, omita."
    )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


if __name__ == "__main__":
    result = ask(" ".join(sys.argv[1:]) or "quantas partidas há no banco?")
    print("SQL:", result["sql"])
    print(result["columns"])
    for row in result["rows"][:20]:
        print(row)
