"""Validação da interface em linguagem natural (apontamento da banca).

Metodologia: conjunto fixo de perguntas de referência com SQL "gold".
Para cada pergunta, compara o RESULTADO da query gerada com o resultado
da query de referência (comparação por resultado é mais justa que por
texto, pois SQLs diferentes podem ser equivalentes).

Métrica: taxa de acerto (execution accuracy), reportável no TCC II.

Uso:  python -m src.nlq.evaluate_nlq

Grava: reports/nlq_benchmark.json — accuracy, base, modelo e o desfecho de
cada pergunta (SQL de referência, SQL gerada e a causa da falha quando houver).

O arquivo passou a ser gravado em 2026-10-04 porque o Apêndice B do TCC
publicava 23/26 sem artefato nenhum: o script so imprimia, e o numero vivia
na saida de console e no diario. O JSON carrega a contagem de partidas da
fila 420 porque um benchmark sem base declarada nao diz sobre o que ele
mediu.

NAO GRAVA EM RUN DEGENERADO. `_degenerado()` recusa a rodada quando nenhum
acerto sai ou quando todas as perguntas falham com a mesma causa — o caso de
`ANTHROPIC_API_KEY` ausente, em que `generate_sql` estoura `KeyError` nas 26.
Sem essa guarda, rodar o comando num ambiente quebrado gravaria 0/26 e
SOBRESCREVERIA a ultima medicao boa com um arquivo que tem cara de medicao.
Run quebrado preserva o artefato anterior e sai com codigo 1.
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


# O nome do modelo fica declarado aqui porque o artefato precisa dizer
# sobre qual modelo a medicao foi feita, e o `model` e passado
# explicitamente ao `generate_sql`. Se o default dele mudar e este
# constante nao, o artefato passa a mentir sobre a medicao.
MODELO_BENCHMARK = "claude-haiku-4-5-20251001"


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

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM matches WHERE queue_id = 420")
        return int(cur.fetchone()[0])


# Abaixo disto a rodada nao e sobre o produto. A faixa medida e 85-95% e o
# valor publicado e 88%, entao o corte em 50% fica longe do que se considera
# resultado legitimo: nao e um limiar que aceita o estado atual, e um corte
# para separar "a plataforma respondeu" de "o ambiente nao deixou responder".
MINIMO_PLAUSIVEL = 0.5


def _degenerado(hits: int, erros: list[str]) -> str:
    """Diz por que a rodada nao e medicao, e devolve "" quando e medicao.

    ESTA FUNCAO E O QUE IMPEDE O ARTEFATO DE MENTIR. Sem ela, rodar o comando
    num ambiente quebrado — sem `ANTHROPIC_API_KEY`, cota estourada, banco
    fora — produz 0/26 e `write_text` SOBRESCREVE o artefato bom anterior com
    um arquivo que tem cara de medicao. E `docs/scripts.md` manda exatamente
    esse caminho: "rode de novo depois de qualquer mudanca".

    Tres criterios:

    - nenhum acerto: nao mediu nada;
    - accuracy abaixo de `MINIMO_PLAUSIVEL`: nenhuma plataforma que responda
      85-95% das perguntas produz 4/26;
    - tres ou mais falhas com a MESMA causa: e ambiente, nao pergunta. Cobre
      a cota que acaba no meio da rodada, em que as primeiras perguntas
      passam e as seguintes falham igual — e esse caso nao se enxerga no
      total, so nas causas.

    O Apêndice B já documenta uma rodada de 22/26 em que a falha extra era
    ruido de leitura sob escrita concorrente: o ruido de uma rodada e
    justamente o que nao deve virar arquivo.
    """
    total = len(erros) or 1
    if hits == 0:
        return "nenhum acerto: a rodada nao mediu nada"
    if hits / total < MINIMO_PLAUSIVEL:
        return (f"accuracy {hits}/{total} abaixo de "
                f"{MINIMO_PLAUSIVEL:.0%}: ambiente, nao produto")
    causas = [e for e in erros if e]
    if len(causas) >= 3 and len(set(causas)) == 1:
        return (f"{len(causas)} falhas com a mesma causa "
                f"({causas[0][:60]!r}): ambiente, nao pergunta")
    return ""


def main() -> None:
    hits = 0
    detalhe: list[dict] = []
    for i, (question, gold_sql) in enumerate(BENCHMARK, 1):
        sql_gerada = ""
        erro = ""
        erro_sql = ""
        erro_causa = ""
        try:
            sql_gerada = generate_sql(question, model=MODELO_BENCHMARK)
            validate_sql(sql_gerada)
            _, gen_rows = run_query(sql_gerada)
            _, gold_rows = run_query(gold_sql)
            ok = normalize(gen_rows) == normalize(gold_rows)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERRO] {question} -> {exc}")
            erro = str(exc)
            # SqlExecutionError carrega a SQL e a causa original para o
            # usuario poder depurar (ver nl_to_sql). `str(exc)` devolve so a
            # causa, porque a classe chama super().__init__(str(cause)) — sem
            # isto o artefato guarda a falha sem a SQL que a produziu.
            erro_sql = getattr(exc, "sql", "") or ""
            erro_causa = repr(getattr(exc, "cause", exc))
            ok = False
        hits += ok
        detalhe.append({"n": i, "pergunta": question,
                        "sql_referencia": " ".join(gold_sql.split()),
                        "sql_gerada": sql_gerada,
                        "ok": bool(ok), "erro": erro,
                        "erro_sql": erro_sql, "erro_causa": erro_causa})
        print(f"[{'OK' if ok else 'FALHA'}] {question}")
    print(f"\nExecution accuracy: {hits}/{len(BENCHMARK)} = {hits/len(BENCHMARK):.0%}")

    destino = Path(__file__).resolve().parent.parent.parent / "reports"
    destino.mkdir(parents=True, exist_ok=True)
    arquivo = destino / "nlq_benchmark.json"

    motivo = _degenerado(hits, [d["erro"] for d in detalhe])
    if motivo:
        # Preserva o artefato anterior em vez de sobrescrever. Um run quebrado
        # nao pode apagar a ultima medicao boa — mesmo principio de
        # idempotencia que vale para os coletores e os ETLs do projeto.
        print(f"\nNAO GRAVADO — {motivo}.")
        if arquivo.exists():
            print(f"O artefato anterior ({arquivo}) foi preservado.")
        raise SystemExit(1)

    doc = {
        "medido_em": date.today().isoformat(),
        "base_partidas_fila_420": _contagem_partidas(),
        "total_perguntas": len(BENCHMARK),
        "acertos": hits,
        "execution_accuracy": round(hits / len(BENCHMARK), 4),
        "modelo": MODELO_BENCHMARK,
        "metodo": "comparacao do RESULTADO da query gerada com o da query "
                  "de referencia (execution accuracy), nao do texto da SQL",
        "detalhe": detalhe,
    }
    # Grava em temporario e troca: um `write_text` interrompido deixaria o
    # arquivo pela metade, e JSON pela metade nao serve nem para diagnostico.
    temporario = arquivo.with_suffix(".json.tmp")
    temporario.write_text(json.dumps(doc, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    temporario.replace(arquivo)
    print(f"gravado: {arquivo}")


if __name__ == "__main__":
    main()
