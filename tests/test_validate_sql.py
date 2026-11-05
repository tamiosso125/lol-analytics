"""Testes do validador de SQL do text-to-SQL (src/nlq/sql_guard.py).

Não precisa de banco nem de chave da Anthropic: só valida texto, nunca executa.

Três grupos:
  * DEVE PASSAR: consultas legítimas, incluindo as que a versão antiga recusava
    por engano (EXTRACT/TRIM/SUBSTRING com FROM);
  * DEVE BLOQUEAR: escrita, várias instruções, tabela fora da lista por qualquer
    caminho (vírgula, aspas, subconsulta, parênteses, função na posição de
    tabela), funções perigosas, SELECT INTO, FOR UPDATE, comentário, `$`;
  * REGRESSÃO: as 26 SQL de referência e as 26 geradas do benchmark
    (`reports/nlq_benchmark.json`) continuam passando.

Uso:  .venv\\Scripts\\python.exe tests\\test_validate_sql.py
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.nlq.sql_guard import validate_sql  # noqa: E402

DEVE_PASSAR = {
    "contagem simples": "SELECT COUNT(*) FROM matches",
    "com ponto e vírgula final": "SELECT COUNT(*) FROM matches;",
    "extract de coluna": "SELECT EXTRACT(YEAR FROM m.game_creation) AS ano, COUNT(*) FROM matches m GROUP BY ano",
    "extract de função": "SELECT EXTRACT(YEAR FROM to_timestamp(1700000000)) FROM matches LIMIT 1",
    "extract com subconsulta permitida": "SELECT EXTRACT(YEAR FROM (SELECT MAX(game_creation) FROM matches)) AS ano",
    "substring": "SELECT SUBSTRING(game_version FROM 1 FOR 5) FROM matches LIMIT 5",
    "trim": "SELECT TRIM(BOTH 'x' FROM champion_name) FROM participants LIMIT 5",
    "join com alias": "SELECT t.team_id, AVG(t.win::int) FROM matches m JOIN teams t ON t.match_id = m.match_id GROUP BY t.team_id",
    "join com using": "SELECT COUNT(*) FROM matches JOIN teams USING (match_id)",
    "vários joins": "SELECT COUNT(*) FROM participants p JOIN matches m ON m.match_id = p.match_id JOIN teams t ON t.match_id = m.match_id AND t.team_id = p.team_id",
    "junção por vírgula entre tabelas permitidas": "SELECT COUNT(*) FROM teams t, matches m WHERE t.match_id = m.match_id",
    "exists correlacionado": "SELECT COUNT(*) FROM participants p WHERE EXISTS (SELECT 1 FROM participants a WHERE a.match_id = p.match_id AND a.team_id = p.team_id)",
    "in com subconsulta": "SELECT COUNT(*) FROM teams WHERE match_id IN (SELECT match_id FROM matches WHERE queue_id = 420)",
    "subconsulta no from": "SELECT AVG(n) FROM (SELECT COUNT(*) AS n FROM participants GROUP BY match_id) x",
    "cte": "WITH c AS (SELECT match_id FROM matches) SELECT COUNT(*) FROM c JOIN teams USING (match_id)",
    "duas ctes": "WITH a AS (SELECT match_id FROM matches), b AS (SELECT match_id FROM teams) SELECT COUNT(*) FROM a JOIN b USING (match_id)",
    "janela": "SELECT champion_name, ROW_NUMBER() OVER (PARTITION BY team_position ORDER BY kills DESC) FROM participants LIMIT 10",
    "tabelas do competitivo": "SELECT pg.league, COUNT(DISTINCT pg.game_id) FROM pro_games pg JOIN pro_players pp ON pp.game_id = pg.game_id AND pp.side = pg.side GROUP BY pg.league",
    "schema public": "SELECT COUNT(*) FROM public.matches",
    "recusa com ponto e vírgula dentro do texto": "SELECT 'não é possível responder: falta dado; não existe' AS aviso;",
    "aspas simples com palavra proibida dentro do texto": "SELECT 'insert into drop' AS aviso",
    "palavra parecida com proibida": "SELECT updated_at FROM players LIMIT 1",
    "maiúsculas e minúsculas": "select count(*) from MATCHES",
    "quebra de linha": "SELECT COUNT(*)\nFROM matches\nWHERE queue_id = 420",
}

DEVE_BLOQUEAR = {
    "escrita": "DELETE FROM matches",
    "insert dentro de select": "SELECT 1; INSERT INTO matches VALUES (1)",
    "dois statements": "SELECT 1; SELECT 2",
    "não começa com select": "EXPLAIN ANALYZE SELECT 1",
    "select into cria tabela": "SELECT * INTO nova FROM matches",
    "for update": "SELECT * FROM matches FOR UPDATE",
    "tabela fora da lista": "SELECT * FROM pg_user",
    "catálogo": "SELECT * FROM information_schema.tables",
    "schema pg_catalog": "SELECT * FROM pg_catalog.pg_user",
    "junção por vírgula com tabela fora": "SELECT * FROM matches m, pg_user u",
    "junção por vírgula, três itens": "SELECT * FROM matches m, teams t, pg_user u",
    "identificador entre aspas": 'SELECT * FROM "pg_user"',
    "aspas na junção": 'SELECT * FROM matches JOIN "pg_user" ON true',
    "lateral": "SELECT * FROM matches m, LATERAL (SELECT * FROM pg_shadow) x",
    "parênteses com junção": "SELECT * FROM (pg_user u JOIN matches m ON true)",
    "subconsulta com tabela fora no from": "SELECT * FROM (SELECT * FROM pg_user) x",
    "subconsulta com tabela fora no where": "SELECT 1 FROM matches WHERE EXISTS (SELECT 1 FROM pg_user)",
    "tabela fora escondida em extract": "SELECT EXTRACT(YEAR FROM (SELECT now() FROM pg_user LIMIT 1))",
    "tabela fora na segunda junção": "SELECT * FROM matches JOIN teams USING (match_id) JOIN pg_user ON true",
    "tabela fora depois de cte": "WITH c AS (SELECT 1) SELECT * FROM c, pg_user",
    "função na posição de tabela": "SELECT * FROM generate_series(1, 10)",
    "values na posição de tabela": "SELECT * FROM (VALUES (1)) v",
    "unnest": "SELECT * FROM unnest(ARRAY[1,2])",
    "leitura de arquivo": "SELECT pg_read_file('/etc/hosts')",
    "listagem de diretório": "SELECT pg_ls_dir('.')",
    "objeto grande": "SELECT lo_import('/etc/hosts')",
    "sleep": "SELECT pg_sleep(5)",
    "executa sql como texto": "SELECT query_to_xml('select * from pg_user', true, false, '')",
    "dblink": "SELECT dblink('host=x', 'select 1')",
    "set_config": "SELECT set_config('statement_timeout', '0', false)",
    "derruba sessão": "SELECT pg_terminate_backend(1)",
    "comentário de linha": "SELECT 1 FROM matches -- , pg_user",
    "comentário de bloco": "SELECT * FROM matches/**/, pg_user",
    "dollar quoting": "SELECT $$x$$ FROM matches",
    "barra invertida": "SELECT E'\\x41' FROM matches",
    "nextval": "SELECT nextval('s')",
}


def main() -> int:
    falhas = []
    for nome, sql in DEVE_PASSAR.items():
        try:
            validate_sql(sql)
        except ValueError as exc:
            falhas.append(f"DEVIA PASSAR: {nome} -> {exc}")
    for nome, sql in DEVE_BLOQUEAR.items():
        try:
            validate_sql(sql)
            falhas.append(f"DEVIA BLOQUEAR: {nome}")
        except ValueError:
            pass

    bench = RAIZ / "reports" / "nlq_benchmark.json"
    n_corpus = 0
    if bench.exists():
        for p in json.loads(bench.read_text(encoding="utf-8"))["detalhe"]:
            for campo in ("sql_referencia", "sql_gerada"):
                sql = p.get(campo)
                if not sql:
                    continue
                n_corpus += 1
                try:
                    validate_sql(sql)
                except ValueError as exc:
                    falhas.append(f"REGRESSAO pergunta {p['n']} ({campo}): {exc}")
    else:
        falhas.append("REGRESSAO: reports/nlq_benchmark.json nao existe")

    print(f"{len(DEVE_PASSAR)} devem passar, {len(DEVE_BLOQUEAR)} devem bloquear, {n_corpus} do benchmark")
    for f in falhas:
        print("  FALHA:", f)
    print("OK" if not falhas else f"{len(falhas)} FALHA(S)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
