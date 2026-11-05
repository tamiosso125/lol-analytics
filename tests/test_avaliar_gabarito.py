"""Testa o comparador do gabarito (src/nlq/avaliar_gabarito.py), sem banco nem API.

Cada caso é uma decisão de regra: tolerância numérica, fração × percentual, ranking por
posição, recusa esperada, base errada. Se uma regra mudar, o teste muda junto.

Uso:  python tests/test_avaliar_gabarito.py (com a .venv)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.nlq.avaliar_gabarito import bate_escalar, bate_ranking, e_recusa, julgar, wilson

print("comparador do gabarito")

# escalar: tolerância, tipo, coluna extra, fração × percentual
assert bate_escalar([[0.5289575]], [["Sylas", "0.52895752895752895753"]])
assert bate_escalar([[0.5289575]], [[53.5]]) is False          # 53,5 está fora da tolerância de 0,1%
assert bate_escalar([[0.5289575]], [[52.89575]])
assert bate_escalar([[1234]], [[1234.0]])
assert not bate_escalar([[1234]], [[1300]])
assert not bate_escalar([[10]], [])
assert bate_escalar([["TOP"]], [["top", 5]])                    # texto, sem acento nem caixa

# ranking: chave na mesma posição; colunas extras e linhas extras no fim ok
ref = [["Jayce", 7336], ["LeeSin", 7201], ["Sylas", 7192]]
assert bate_ranking(ref, [["Jayce", 7336, "x"], ["LeeSin", 1], ["Sylas", 2], ["Ezreal", 3]])
assert not bate_ranking(ref, [["LeeSin", 1], ["Jayce", 2], ["Sylas", 3]])   # ordem trocada
assert not bate_ranking(ref, [["Jayce", 1], ["LeeSin", 2]])                  # faltou linha

# recusa
rec = {"base": "competitivo", "sql": "SELECT 'não é possível responder: x' AS aviso;", "erro": None, "rows": [["x"]]}
num = {"base": "competitivo", "sql": "SELECT 1", "erro": None, "rows": [[1]]}
assert e_recusa(rec) and not e_recusa(num)
item_rec = {"recusa_esperada": True, "base": "competitivo", "tipo": "recusa"}
assert julgar(item_rec, {"status": "respondeu", "resultados": [rec]}, None)["passou"]
assert not julgar(item_rec, {"status": "respondeu", "resultados": [num]}, None)["passou"]
# uma base recusou e a outra inventou: falha
assert not julgar(item_rec, {"status": "respondeu", "resultados": [rec, {**num, "base": "solo"}]}, None)["passou"]

# respondível: base certa, base errada, recusa indevida, erro
item = {"recusa_esperada": False, "base": "competitivo", "tipo": "escalar"}
ok = {"status": "respondeu", "resultados": [{**num, "rows": [[42]]}]}
assert julgar(item, ok, [[42]])["passou"]
assert not julgar(item, ok, [[43]])["passou"]
assert not julgar(item, {"status": "respondeu", "resultados": [{**num, "base": "solo", "rows": [[42]]}]}, [[42]])["passou"]
assert julgar(item, {"status": "respondeu", "resultados": [rec]}, [[42]])["motivo"].startswith("recusa indevida")
assert not julgar(item, {"status": "erro", "erro": {"tipo": "execucao"}}, [[42]])["passou"]
# AMBOS: basta a base esperada bater
assert julgar(item, {"status": "respondeu", "resultados": [{**num, "base": "solo", "rows": [[1]]}, {**num, "rows": [[42]]}]}, [[42]])["passou"]

lo, hi = wilson(88, 100)
assert 80 < lo < 81 and 92 < hi < 94
print("OK")
