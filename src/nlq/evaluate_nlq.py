"""Validação da interface em linguagem natural (apontamento da banca).

Metodologia: conjunto fixo de perguntas de referência com SQL "gold".
Para cada pergunta, compara o RESULTADO da query gerada com o resultado
da query de referência (comparação por resultado é mais justa que por
texto, pois SQLs diferentes podem ser equivalentes).

Métrica: taxa de acerto (execution accuracy), reportável no TCC II.

Uso:  python -m src.nlq.evaluate_nlq

Grava: reports/nlq_benchmark.json

O arquivo passou a ser gravado em 2026-10-04 porque o Apêndice B do TCC
publicava 23/26 sem artefato nenhum: o script so imprimia, e o numero vivia
na saida de console e no diario. O JSON carrega a contagem de partidas da
fila 420 porque um benchmark sem base declarada nao diz sobre o que ele
mediu.
"""
import json
from datetime import date
from pathlib import Path

from src.nlq.nl_to_sql import generate_sql, run_query, validate_sql

# >= 20 perguntas (exigência da banca), cobrindo agregações simples,
# joins, filtros por posição/campeão/tier e perguntas sobre objetivos.
BENCHMARK: list[tuple[str, str]] = [
    (
        "Quantas partidas existem no banco?",
        "SELECT COUNT(*) FROM matches",
    ),
    (
        "Quais os 5 campeões mais jogados?",
        """SELECT champion_name, COUNT(*) AS n FROM participants
           GROUP BY champion_name ORDER BY n DESC LIMIT 5""",
    ),
    (
        "Qual o win rate do time azul?",
        "SELECT AVG(win::int) FROM teams WHERE team_id = 100",
    ),
    (
        "Qual a duração média das partidas em minutos?",
        "SELECT AVG(game_duration_s) / 60.0 FROM matches",
    ),
    (
        "Quais os 5 campeões com maior win rate com pelo menos 50 jogos?",
        """SELECT champion_name, AVG(win::int) AS wr FROM participants
           GROUP BY champion_name HAVING COUNT(*) >= 50
           ORDER BY wr DESC LIMIT 5""",
    ),
    (
        "Quantos jogadores estão cadastrados na tabela de jogadores?",
        "SELECT COUNT(*) FROM players",
    ),
    (
        "Quantas partidas o time vermelho venceu?",
        "SELECT COUNT(*) FROM teams WHERE team_id = 200 AND win = true",
    ),
    (
        "Qual a média de ouro (gold_earned) dos jogadores na posição JUNGLE?",
        "SELECT AVG(gold_earned) FROM participants WHERE team_position = 'JUNGLE'",
    ),
    (
        "Quais os 5 campeões mais jogados na posição MIDDLE?",
        """SELECT champion_name, COUNT(*) AS n FROM participants
           WHERE team_position = 'MIDDLE' GROUP BY champion_name
           ORDER BY n DESC LIMIT 5""",
    ),
    (
        "Qual o win rate por posição?",
        """SELECT team_position, AVG(win::int) AS wr FROM participants
           GROUP BY team_position ORDER BY wr DESC""",
    ),
    (
        "Qual a média de barões derrubados pelo time vencedor por partida?",
        "SELECT AVG(barons) FROM teams WHERE win = true",
    ),
    (
        "Qual o campeão com maior win rate jogando na posição UTILITY, com pelo menos 20 partidas?",
        """SELECT champion_name, AVG(win::int) AS wr FROM participants
           WHERE team_position = 'UTILITY' GROUP BY champion_name
           HAVING COUNT(*) >= 20 ORDER BY wr DESC LIMIT 1""",
    ),
    (
        "Quantas partidas duraram mais de 30 minutos?",
        "SELECT COUNT(*) FROM matches WHERE game_duration_s > 1800",
    ),
    (
        "Qual a média de dano causado a campeões pelos jogadores do time azul?",
        "SELECT AVG(dmg_to_champions) FROM participants WHERE team_id = 100",
    ),
    (
        "Quantos jogadores estão no tier Challenger?",
        "SELECT COUNT(*) FROM players WHERE tier = 'CHALLENGER'",
    ),
    (
        "Qual time, azul ou vermelho, derruba mais torres em média?",
        """SELECT team_id, AVG(towers) AS avg_towers FROM teams
           GROUP BY team_id ORDER BY avg_towers DESC LIMIT 1""",
    ),
    (
        "Quantas partidas existem por versão do jogo, da mais para a menos frequente?",
        """SELECT game_version, COUNT(*) AS n FROM matches
           GROUP BY game_version ORDER BY n DESC""",
    ),
    (
        "Qual o CS (farm) médio dos jogadores na posição TOP?",
        "SELECT AVG(cs_total) FROM participants WHERE team_position = 'TOP'",
    ),
    (
        "Quais os 5 campeões com maior média de assistências?",
        """SELECT champion_name, AVG(assists) AS avg_assists FROM participants
           GROUP BY champion_name ORDER BY avg_assists DESC LIMIT 5""",
    ),
    (
        "Em quantas partidas o time que conquistou pelo menos um arauto também venceu?",
        "SELECT COUNT(*) FROM teams WHERE heralds > 0 AND win = true",
    ),
    (
        "Quantas partidas têm participantes que também estão na tabela de jogadores?",
        """SELECT COUNT(DISTINCT pt.match_id) FROM participants pt
           JOIN players p ON p.puuid = pt.puuid""",
    ),
    (
        "Qual o campeão com maior win rate entre os jogadores do tier Grandmaster, com pelo menos 10 partidas?",
        """SELECT pt.champion_name, AVG(pt.win::int) AS wr
           FROM participants pt JOIN players p ON p.puuid = pt.puuid
           WHERE p.tier = 'GRANDMASTER'
           GROUP BY pt.champion_name HAVING COUNT(*) >= 10
           ORDER BY wr DESC LIMIT 1""",
    ),
    # ---- competitivo (pro play, Oracle's Elixir) ----
    (
        "Quantos jogos profissionais de 2026 existem no banco?",
        "SELECT COUNT(DISTINCT game_id) FROM pro_games WHERE year = 2026",
    ),
    (
        "Qual o win rate do lado azul no competitivo em 2026?",
        "SELECT AVG(win::int) FROM pro_games WHERE side = 'Blue' AND year = 2026",
    ),
    (
        "Quais os 5 campeões mais jogados no competitivo em 2026?",
        """SELECT pp.champion, COUNT(*) AS jogos
           FROM pro_players pp
           JOIN pro_games pg ON pg.game_id = pp.game_id AND pg.side = pp.side
           WHERE pg.year = 2026
           GROUP BY pp.champion ORDER BY jogos DESC LIMIT 5""",
    ),
    (
        "Qual liga teve mais jogos profissionais em 2026?",
        """SELECT league, COUNT(DISTINCT game_id) AS jogos
           FROM pro_games WHERE year = 2026
           GROUP BY league ORDER BY jogos DESC LIMIT 1""",
    ),
]


def normalize(rows: list[tuple]) -> set:
    out = set()
    for row in rows:
        norm = tuple(
            round(float(v), 3) if isinstance(v, (int, float)) and not isinstance(v, bool)
            else v
            for v in row
        )
        out.add(norm)
    return out


def _contagem_partidas() -> int:
    """Partidas na fila ranqueada, que e a base que o TCC declara.

    Sem isto o artefato nao diz sobre quantas partidas o benchmark rodou, e
    um benchmark sem base declarada e o problema que a nota de duas bases do
    TCC acabou de passar a vida inteira evitando.
    """
    from src.db import get_conn

    cur = get_conn().cursor()
    cur.execute("SELECT COUNT(*) FROM matches WHERE queue_id = 420")
    return int(cur.fetchone()[0])


def main() -> None:
    hits = 0
    detalhe = []
    for i, (question, gold_sql) in enumerate(BENCHMARK, 1):
        erro = ""
        try:
            gen_sql = generate_sql(question)
            validate_sql(gen_sql)
            _, gen_rows = run_query(gen_sql)
            _, gold_rows = run_query(gold_sql)
            ok = normalize(gen_rows) == normalize(gold_rows)
        except Exception as exc:
            print(f"[ERRO] {question} -> {exc}")
            erro = str(exc)
            ok = False
        hits += ok
        detalhe.append({"n": i, "pergunta": question,
                        "sql_referencia": " ".join(gold_sql.split()),
                        "ok": bool(ok), "erro": erro})
        print(f"[{'OK' if ok else 'FALHA'}] {question}")
    print(f"\nExecution accuracy: {hits}/{len(BENCHMARK)} = {hits/len(BENCHMARK):.0%}")

    # Arquiva o resultado. O script antes so imprimia, e o Apêndice B do TCC
    # publicava um numero sem artefato — a mesma lacuna que o diario
    # registrou para o tune_models em 2026-10-04 e que la foi resolvida
    # criando um script que grava. Um numero de TCC que so vive na saida de
    # console nao e reproduzivel por ninguem que nao esteja na minha sessao.
    destino = Path(__file__).resolve().parent.parent.parent / "reports"
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / "nlq_benchmark.json"
    base = _contagem_partidas()
    arquivo.write_text(
        json.dumps({
            "medido_em": date.today().isoformat(),
            "base_partidas_fila_420": base,
            "total_perguntas": len(BENCHMARK),
            "acertos": hits,
            "execution_accuracy": round(hits / len(BENCHMARK), 4),
            "metodo": "comparacao do RESULTADO da query gerada com o da query "
                      "de referencia (execution accuracy), nao do texto da SQL",
            "detalhe": detalhe,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"gravado: {arquivo}")


if __name__ == "__main__":
    main()
