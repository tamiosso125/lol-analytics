"""Testa a resolução de nomes (src/nlq/entidades.py) e a checagem 'eliminações = kills'
(src/nlq/nl_to_sql.py), sem banco nem API: o índice é injetado.

Uso:  python tests/test_entidades.py (com a .venv)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.nlq.entidades import dica, encontrar, normalizar, so_do_competitivo
from src.nlq.nl_to_sql import soma_assist_indevida

print("resolução de nomes e eliminações")

def idx(*itens):
    d = {}
    for tipo, nome, base in itens:
        d.setdefault(normalizar(nome), []).append((tipo, nome, base))
    return d

IDX = idx(("campeao", "MonkeyKing", "solo"), ("campeao", "Locke", "solo"), ("campeao", "Cho'Gath", "competitivo"),
          ("campeao", "Chogath", "solo"), ("liga", "LPLOL", "competitivo"), ("liga", "AL", "competitivo"),
          ("liga", "LPL", "competitivo"), ("equipe", "RED Canids", "competitivo"), ("equipe", "inf", "competitivo"),
          ("equipe", "Priority", "competitivo"), ("jogador", "H4cker", "competitivo"))

assert normalizar("Cho'Gath") == "chogath" and normalizar("Monkey King") == "monkeyking"

# grafia diferente da escrita na pergunta vira o nome exato do banco
achou = encontrar("Qual a média do campeão Monkey King?", IDX)
assert [a["nome"] for a in achou] == ["MonkeyKing"], achou
assert "'Locke'" in dica("média de eliminações do campeão Locke", "solo", IDX)
# liga não é equipe; a maior sequência vence ("RED Canids" e não "red")
assert [a["tipo"] for a in encontrar("Quantos jogos a LPLOL teve em 2026?", IDX)] == ["liga"]
assert [a["nome"] for a in encontrar("taxa de vitória da equipe RED Canids em 2026", IDX)] == ["RED Canids"]
# duas letras só em maiúsculas: "em" minúsculo é preposição, "AL" é a liga
assert [a["nome"] for a in encontrar("duração média da AL em 2026", IDX)] == ["AL"]
assert encontrar("jogos em 2026", IDX) == []
# palavras comuns não viram nome
assert encontrar("Qual equipe teve a maior taxa de vitória", IDX) == []
# a dica só traz entidades da base consultada
assert "pro_players.champion" in dica("média do Cho'Gath", "competitivo", IDX)
assert dica("média do Chogath", "solo", IDX).count("participants.champion_name") == 1
# pista de roteamento
assert so_do_competitivo("Quantos jogos o jogador H4cker disputou?", IDX)
assert not so_do_competitivo("Qual a taxa de vitória do campeão Locke?", IDX)

# eliminações = kills
assert soma_assist_indevida("Quais os 3 campeões com maior média de eliminações no MIDDLE?",
                            "SELECT AVG(p.kills + p.assists) FROM participants p")
assert not soma_assist_indevida("Qual a participação nas eliminações da equipe?", "SELECT AVG(kills + assists) FROM t")
assert not soma_assist_indevida("Qual o KDA médio?", "SELECT AVG((kills + assists)::float/deaths) FROM t")
assert not soma_assist_indevida("Qual a média de eliminações?", "SELECT AVG(kills) FROM t")
print("OK")
