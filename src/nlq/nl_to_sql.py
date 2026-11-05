"""Interface em linguagem natural (objetivo específico g do TCC).

Abordagem: text-to-SQL — o LLM recebe o schema e a pergunta do usuário
e gera uma query SELECT, que é validada antes da execução.

Camadas de segurança (as três primeiras em sql_guard.py, reescritas em
2026-11-04 com falha fechada; ver o docstring de lá):
  1. apenas um statement, começando com SELECT ou WITH (sem ; encadeado);
  2. palavras-chave de escrita e funções perigosas bloqueadas;
  3. somente tabelas do schema são permitidas (inclusive em junção por vírgula,
     subconsulta e parênteses; sem nome entre aspas);
  4. statement_timeout no PostgreSQL.

Requer ANTHROPIC_API_KEY no ambiente (.env).

Uso:  python -m src.nlq.nl_to_sql "qual campeão tem maior win rate?"
"""
import os
import sys

import anthropic
import psycopg2

from src.db import get_conn
from src.nlq.schema_context import SCHEMA_DESCRIPTION

# a validação (camadas 1 a 3) vive em sql_guard.py, testável sem banco nem chave:
# tests/test_validate_sql.py. Reexportada aqui porque evaluate_nlq e a API importam daqui.
from src.nlq.route import AMBOS, PRO, SOLO, rotear  # noqa: E402
from src.nlq.sql_guard import (  # noqa: E402,F401
    ALLOWED_TABLES, FORBIDDEN, BaseMixError, validate_base, validate_sql,
)

# dica de base na MENSAGEM do usuário (o esquema no prompt de sistema não muda, então
# o benchmark `evaluate_nlq`, que não passa base, é exatamente o mesmo de antes)
DICA_BASE = {
    "solo": (
        "[Base escolhida: SOLO QUEUE. Use somente as tabelas matches, teams, participants, "
        "players, bans, item_events e items. Não use pro_games nem pro_players.]"
    ),
    "competitivo": (
        "[Base escolhida: COMPETITIVO (profissional). Use somente pro_games e pro_players. "
        "Não use matches, teams, participants, players, bans, item_events nem items.]"
    ),
}


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
    erro_anterior: tuple[str, str] | None = None,
    base: str | None = None,
) -> str:
    """history: turnos anteriores da mesma conversa, cada um
    {"question": ..., "sql": ...} — dá contexto para perguntas de
    acompanhamento ("agora filtre só os challenger").

    erro_anterior: (sql, mensagem do banco) da tentativa que falhou ao executar.
    Só `ask` usa, uma vez; o benchmark (`evaluate_nlq`) não, de propósito: ele
    mede a primeira tentativa.

    base: "solo" ou "competitivo" quando o roteador (src/nlq/route.py) já decidiu a
    base; a dica vai junto da pergunta. None = sem dica (comportamento de sempre)."""
    messages = []
    for turn in history or []:
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["sql"]})
    pergunta = f"{DICA_BASE[base]}\n\n{question}" if base in DICA_BASE else question
    messages.append({"role": "user", "content": pergunta})
    if erro_anterior:
        sql_ruim, erro = erro_anterior
        messages.append({"role": "assistant", "content": sql_ruim})
        messages.append({
            "role": "user",
            "content": (
                "Essa consulta falhou ao executar no PostgreSQL com este erro:\n"
                f"{erro}\n"
                "Corrija a consulta, mantendo o que a pergunta pede, e responda apenas "
                "com a SQL (um SELECT). Se o schema não tem o dado pedido, use o aviso "
                "de 'não é possível responder'."
            ),
        })

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
    return extrair_sql(msg.content[0].text)


def extrair_sql(texto: str) -> str:
    """Tira a SQL da resposta do modelo.

    2026-11-05: às vezes o modelo escreve uma SQL, comenta "Wait, let me reconsider" e
    escreve outra; a segunda é a corrigida. Antes, o texto inteiro ia ao validador e
    voltava "Múltiplos statements" (4 de 4 passadas do cego, pergunta 86). Quando há
    blocos de código, vale o ÚLTIMO que começa com SELECT ou WITH; o validador
    continua sendo aplicado a ele como a qualquer SQL."""
    texto = texto.strip()
    if "```" in texto:
        candidatos = []
        for parte in texto.split("```"):
            p = parte.strip()
            if p.lower().startswith("sql"):
                p = p[3:].strip()
            if p.lower().startswith(("select", "with")):
                candidatos.append(p)
        if candidatos:
            return candidatos[-1]
    return texto.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()


def run_query(sql: str) -> tuple[list[str], list[tuple]]:
    with get_conn() as conn:
        # 2026-11-05: defesa em profundidade. Se o validador falhar, o próprio banco
        # recusa escrita (a conexão só tinha statement_timeout). Precisa vir antes de
        # qualquer comando da transação.
        conn.set_session(readonly=True)
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '10s'")
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            return cols, cur.fetchall()


def ask_base(question: str, history: list[dict] | None = None, base: str | None = None) -> dict:
    """Gera, valida e executa numa base ("solo", "competitivo" ou None = sem base).

    Se o banco rejeitar a SQL (coluna inexistente, agregação aninhada, tipo
    errado...) OU a SQL misturar as duas bases, faz UMA nova tentativa passando o
    erro ao modelo (2026-11-04: 4 de 50 perguntas livres falharam por erro de SQL).
    A nova SQL passa por `validate_sql` e pela guarda de base como qualquer outra,
    a temperatura continua 0 e o resultado devolve a SQL que de fato rodou, com
    `tentativas` = 2. Se a segunda também falhar, levanta SqlExecutionError (ou
    BaseMixError) com a SQL e a causa da ÚLTIMA tentativa, encadeada à primeira
    (`__cause__`): o erro não é engolido. Estouro de tempo (`statement_timeout`)
    não é refeito: repetiria os 10 s e a consulta lenta tende a continuar lenta."""
    sql = generate_sql(question, history, base=base)
    validate_sql(sql)
    try:
        validate_base(sql, base)
        try:
            cols, rows = run_query(sql)
            return {"question": question, "base": base, "sql": sql, "columns": cols,
                    "rows": rows, "tentativas": 1}
        except psycopg2.errors.QueryCanceled as exc:
            raise SqlExecutionError(sql, exc) from exc
        except psycopg2.Error as exc:
            primeiro, erro = exc, str(exc).strip()
    except BaseMixError as exc:
        primeiro, erro = exc, str(exc)
    sql2 = generate_sql(question, history, erro_anterior=(sql, erro), base=base)
    try:
        validate_sql(sql2)
    except ValueError:
        # a correção foi barrada pela validação de segurança: vale o erro real da primeira SQL
        if isinstance(primeiro, BaseMixError):
            raise primeiro from None
        raise SqlExecutionError(sql, primeiro) from primeiro
    validate_base(sql2, base)  # se a correção ainda mistura as bases, levanta BaseMixError
    try:
        cols, rows = run_query(sql2)
    except psycopg2.Error as exc2:
        raise SqlExecutionError(sql2, exc2) from primeiro
    return {"question": question, "base": base, "sql": sql2, "columns": cols, "rows": rows,
            "tentativas": 2}


def _historico_da_base(history: list[dict] | None, base: str) -> list[dict]:
    """Só os turnos dessa base (ou sem base, de versões antigas da tela)."""
    return [t for t in (history or []) if t.get("base") in (None, base)]


def _base_anterior(history: list[dict] | None) -> str | None:
    """Base do último turno, se foi UMA só; None se foi AMBOS ou não se sabe.
    Um turno AMBOS chega como duas entradas com a mesma pergunta, uma por base."""
    if not history:
        return None
    pergunta = history[-1].get("question")
    bases = {t.get("base") for t in history if t.get("question") == pergunta} - {None}
    return next(iter(bases)) if len(bases) == 1 else None


def _erro_de_base(exc: Exception) -> dict:
    """Falha de UMA base, para a resposta mostrar onde falhou sem derrubar a outra."""
    if isinstance(exc, SqlExecutionError):
        tipo = "execucao"
    elif isinstance(exc, BaseMixError):
        tipo = "mistura_de_bases"
    else:
        tipo = "validacao"
    return {"tipo": tipo, "message": str(exc).strip() if tipo != "execucao"
            else "A consulta gerada falhou ao executar no banco.",
            "sql": getattr(exc, "sql", None), "cause": str(getattr(exc, "cause", exc)).strip()}


def ask(question: str, history: list[dict] | None = None, modelo_roteador=None) -> dict:
    """Entrada da API: roteia a pergunta e responde em UMA base ou nas DUAS.

    1. `rotear` decide "solo", "competitivo" ou "ambos" (src/nlq/route.py): sem pista,
       ou com pista dos dois lados, a resposta é AMBOS, nunca um palpite em silêncio.
    2. Cada base roda por `ask_base`, com a dica de base, a guarda de mistura e a nova
       tentativa. Em AMBOS, uma base que falha ou recusa não derruba a outra: o
       resultado dela traz `erro` e a outra aparece normalmente.
    3. Se TODAS as bases falham, levanta a exceção da última (SqlExecutionError,
       BaseMixError ou ValueError), como antes: o erro não é engolido.

    Devolve {"roteamento", "base", "resultados": [...]} e, por compatibilidade com a
    tela antiga, `sql`/`columns`/`rows`/`tentativas` do primeiro resultado que deu certo."""
    roteamento = rotear(question, _base_anterior(history), modelo=modelo_roteador)
    bases = [SOLO, PRO] if roteamento["classe"] == AMBOS else [roteamento["classe"]]
    resultados, ultimo_erro = [], None
    for base in bases:
        try:
            r = ask_base(question, _historico_da_base(history, base), base)
            resultados.append({"base": base, "sql": r["sql"], "columns": r["columns"],
                               "rows": r["rows"], "tentativas": r["tentativas"], "erro": None})
        except (SqlExecutionError, ValueError) as exc:  # BaseMixError é ValueError
            ultimo_erro = exc
            resultados.append({"base": base, "sql": getattr(exc, "sql", None), "columns": [],
                               "rows": [], "tentativas": None, "erro": _erro_de_base(exc)})
    if all(r["erro"] for r in resultados):
        raise ultimo_erro
    primeiro = next(r for r in resultados if not r["erro"])
    return {"question": question, "roteamento": {"classe": roteamento["classe"], "origem": roteamento["origem"]},
            "base": roteamento["classe"], "resultados": resultados,
            "sql": primeiro["sql"], "columns": primeiro["columns"], "rows": primeiro["rows"],
            "tentativas": primeiro["tentativas"]}


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
