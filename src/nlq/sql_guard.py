"""Validação de segurança da SQL gerada pelo LLM (invariante 3 do AGENTS.md).

Camadas, todas obrigatórias (a 4, `statement_timeout`, fica em `run_query`):
  1. um único statement, começando com SELECT ou WITH;
  2. palavras de escrita bloqueadas, e funções perigosas bloqueadas;
  3. só tabelas de ALLOWED_TABLES (e CTEs declaradas na própria consulta);
  4. `statement_timeout` no PostgreSQL.

Reescrito em 2026-11-04. A versão anterior tinha dois problemas, achados ao
rodar 50 perguntas livres e depois sondar o validador (só o texto, sem
executar nada):

  * FALSO POSITIVO: o regex de tabelas lia o `FROM` de `EXTRACT(YEAR FROM x)`
    como tabela e recusava consultas legítimas (6 de 50 perguntas).
  * BURACOS na camada 3, ou seja, consultas que deveriam ser bloqueadas e
    passavam: junção por vírgula (`FROM matches m, pg_user u`), nome entre aspas
    (`FROM "pg_user"`) e funções que executam SQL ou leem arquivo
    (`query_to_xml('select ...')`, `pg_read_file(...)`). O usuário do banco é
    superusuário, então a camada 3 era a única barreira.

Princípio: FALHA FECHADA. O que o analisador não reconhece é recusado, em vez de
liberado. Por isso: sem aspas, sem comentários, sem `$`, sem item de FROM que
não seja tabela simples ou subconsulta, e nenhuma função da lista proibida.

O `FROM` de EXTRACT/TRIM/SUBSTRING/OVERLAY/POSITION não é uma tabela e é
ignorado SÓ no nível de parênteses da própria função: uma subconsulta dentro
deles tem os seus parênteses, e o `FROM` dela continua sendo conferido.
"""
import re

ALLOWED_TABLES = {
    "matches", "teams", "participants", "players", "bans",
    "pro_games", "pro_players", "item_events", "items",
}

# escrita, e `into` (SELECT ... INTO cria tabela) e sequências
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy|into|nextval|setval)\b",
    re.IGNORECASE,
)
# bloqueio de linhas (FOR UPDATE e parentes) também é escrita de fato
LOCKING = re.compile(r"\bfor\s+(update|share|no\s+key\s+update|key\s+share)\b", re.IGNORECASE)

# funções que leem arquivo, executam SQL recebida como texto, mexem na
# configuração ou derrubam sessões. Não basta a lista de tabelas: `SELECT f()`
# não tem FROM.
DANGEROUS_FUNCTIONS = re.compile(
    r"\b(pg_read_file|pg_read_binary_file|pg_ls_\w+|pg_stat_file|pg_file_\w+|lo_\w+|dblink\w*|"
    r"set_config|pg_sleep\w*|pg_terminate_backend|pg_cancel_backend|pg_reload_conf|"
    r"pg_rotate_logfile|pg_switch_wal|pg_promote|pg_create_\w+|pg_drop_\w+|pg_advisory_\w+|"
    r"pg_logical_\w+|pg_replication_\w+|pg_backup_\w+|pg_start_backup|pg_stop_backup|"
    r"query_to_xml\w*|table_to_xml\w*|schema_to_xml\w*|database_to_xml\w*|cursor_to_xml\w*)\b",
    re.IGNORECASE,
)

# `FROM` que pertence a uma função e não introduz tabela
SPECIAL_FROM = {"extract", "trim", "substring", "overlay", "position"}
# palavras que encerram o item de FROM (não são apelido)
STOP_WORDS = {
    "where", "group", "order", "limit", "having", "union", "intersect", "except", "window",
    "offset", "fetch", "returning", "on", "using", "join", "inner", "left", "right", "full",
    "cross", "natural", "lateral", "tablesample", "for", "set", "from", "select", "with",
}

TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_$]*(?:\.[A-Za-z_][A-Za-z0-9_$]*)*|\S")


def _without_string_literals(sql: str) -> str:
    """Remove o conteúdo de literais de string ('...') antes das checagens
    estruturais — evita falso positivo de pontuação/palavras dentro de texto
    livre (ex.: um aviso gerado pelo LLM com ';' na frase)."""
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


def _match_paren(tokens: list[str], i: int) -> int:
    """Índice do ')' que fecha o '(' em tokens[i]; len(tokens) se não fechar."""
    depth = 0
    for j in range(i, len(tokens)):
        if tokens[j] == "(":
            depth += 1
        elif tokens[j] == ")":
            depth -= 1
            if depth == 0:
                return j
    return len(tokens)


def _skip_alias(tokens: list[str], j: int) -> int:
    """Pula `AS apelido` / `apelido` e a lista de colunas `(a, b)` do apelido."""
    n = len(tokens)
    if j < n and tokens[j] == "as":
        j += 1
        if j < n:
            j += 1
    elif j < n and re.fullmatch(r"[a-z_][a-z0-9_$]*", tokens[j]) and tokens[j] not in STOP_WORDS:
        j += 1
    if j < n and tokens[j] == "(":
        j = _match_paren(tokens, j) + 1
    return j


def _from_item(tokens: list[str], j: int, achadas: list[str]) -> int:
    """Lê UM item de FROM/JOIN a partir de tokens[j] e devolve o índice seguinte.
    Tabela simples entra em `achadas`; subconsulta é analisada recursivamente;
    qualquer outra coisa entra como nome inválido (falha fechada)."""
    n = len(tokens)
    while j < n and tokens[j] in ("only", "lateral"):
        j += 1
    if j >= n:
        achadas.append("(from vazio)")
        return j
    if tokens[j] == "(":
        fim = _match_paren(tokens, j)
        interno = tokens[j + 1:fim]
        if interno and interno[0] in ("select", "with"):
            achadas.extend(_referenced_tables(interno))
        else:
            achadas.append("(item de from que nao e subconsulta)")
        return _skip_alias(tokens, fim + 1)
    nome = tokens[j]
    j += 1
    if not re.fullmatch(r"[a-z_][a-z0-9_$]*(?:\.[a-z_][a-z0-9_$]*)*", nome):
        achadas.append(f"({nome})")
        return j
    if j < n and tokens[j] == "(":  # função usada como tabela: generate_series, unnest, values...
        achadas.append(f"{nome}()")
        return _match_paren(tokens, j) + 1
    achadas.append(nome[len("public."):] if nome.startswith("public.") else nome)
    return _skip_alias(tokens, j)


def _referenced_tables(tokens: list[str]) -> list[str]:
    n = len(tokens)
    achadas: list[str] = []
    pilha: list[str] = []  # token que precede cada '(' aberto
    i = 0
    while i < n:
        t = tokens[i]
        if t == "(":
            pilha.append(tokens[i - 1] if i else "")
        elif t == ")":
            if pilha:
                pilha.pop()
        elif t == "from":
            if pilha and pilha[-1] in SPECIAL_FROM:
                i += 1  # FROM de EXTRACT/TRIM/SUBSTRING: não é tabela
                continue
            j = _from_item(tokens, i + 1, achadas)
            while j < n and tokens[j] == ",":  # FROM a, b, c
                j = _from_item(tokens, j + 1, achadas)
            i = max(j, i + 1)
            continue
        elif t == "join":
            i = max(_from_item(tokens, i + 1, achadas), i + 1)
            continue
        i += 1
    return achadas


def validate_sql(sql: str) -> None:
    prefix = sql.lower().lstrip()
    # WITH também é aceito — schema_context.py ensina um exemplo com CTE
    # (item_events/items) e rejeitar isso aqui quebrava a query antes mesmo
    # de checar a allowlist de tabelas.
    if not (prefix.startswith("select") or prefix.startswith("with")):
        raise ValueError("Apenas SELECT (ou WITH ... SELECT) é permitido.")
    structural = _without_string_literals(sql)
    if ";" in structural.rstrip().rstrip(";"):
        raise ValueError("Múltiplos statements não são permitidos.")
    # aspas, comentários, `$` e strings com escape (E'...', U&'...') escondem tokens
    # do analisador, que só entende '...' simples: falha fechada
    if re.search(r"""["`$\\]|--|/\*|\b[eE]''|\b[uU]&""", structural):
        raise ValueError("Identificador entre aspas, comentário ou string especial não são permitidos.")
    if FORBIDDEN.search(structural) or LOCKING.search(structural):
        raise ValueError("Query contém palavra-chave proibida.")
    if DANGEROUS_FUNCTIONS.search(structural):
        raise ValueError("Query usa uma função não permitida.")
    # nomes de CTE (WITH nome AS (...), nome2 AS (...)) não são tabelas do
    # schema — sem isso, uma query com CTE rejeita a si mesma, porque o
    # FROM/JOIN que usa a CTE depois bate na checagem de tabelas.
    cte_names = {
        m.lower() for m in re.findall(r"\b([a-z_][a-z0-9_]*)\s+AS\s*\(", structural, re.IGNORECASE)
    }
    tokens = [t.lower() for t in TOKEN.findall(structural)]
    unknown = set(_referenced_tables(tokens)) - ALLOWED_TABLES - cte_names
    if unknown:
        raise ValueError(f"Tabelas não permitidas: {unknown}")


# --- guarda de base (2026-11-04) ----------------------------------------------------
# O sistema tem duas bases paralelas (docs/plano_roteamento_nlq.md). Uma consulta
# não pode misturá-las: as convenções são diferentes (team_id 100/200 contra
# 'Blue'/'Red'), e a junção teams x pro_games da pergunta 40 devolveu zero linhas.
SOLO_TABLES = {"matches", "teams", "participants", "players", "bans", "item_events", "items"}
PRO_TABLES = {"pro_games", "pro_players"}
BASES = {"solo": SOLO_TABLES, "competitivo": PRO_TABLES}


class BaseMixError(ValueError):
    """A SQL usa tabelas da base que NÃO foi escolhida para a pergunta."""


def tables_used(sql: str) -> set[str]:
    """Tabelas do schema que a SQL referencia (sem as CTEs). Chame DEPOIS de
    `validate_sql`: ela já garantiu que só há tabelas permitidas."""
    structural = _without_string_literals(sql)
    cte_names = {
        m.lower() for m in re.findall(r"\b([a-z_][a-z0-9_]*)\s+AS\s*\(", structural, re.IGNORECASE)
    }
    tokens = [t.lower() for t in TOKEN.findall(structural)]
    return set(_referenced_tables(tokens)) - cte_names


def validate_base(sql: str, base: str | None) -> None:
    """Falha com BaseMixError se a SQL usa tabela fora da base escolhida.
    `base` None não confere nada. Consulta sem tabela (o aviso de "não é possível
    responder") passa em qualquer base."""
    if base not in BASES:
        return
    fora = tables_used(sql) - BASES[base]
    if fora:
        raise BaseMixError(
            f"A consulta é da base '{base}', mas usa tabelas da outra base: {sorted(fora)}"
        )
