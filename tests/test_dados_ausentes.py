"""Testa a recusa determinística de dados ausentes (src/nlq/dados_ausentes.py), sem banco nem API.

Cada padrão é um CONCEITO que o schema não tem; as perguntas abaixo variam a redação.
Também confere que perguntas respondíveis NÃO são barradas (recusa indevida é erro).

Uso:  python tests/test_dados_ausentes.py (com a .venv)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.nlq.dados_ausentes import dado_ausente, sql_de_recusa

print("recusa determinística de dados ausentes")

DEVE_RECUSAR = [
    "Qual equipe conseguiu a primeira torre mais vezes?",
    "Quem pegou o primeiro dragão?",
    "Taxa de vitória de quem fez o primeiro sangue",
    "Qual a média de tempo até o primeiro Barão?",
    "Qual equipe disputou mais séries até o jogo 5?",
    "Quem venceu mais séries melhor de 3?",
    "Qual a diferença de ouro aos 10 minutos?",
    "Qual campeão tem mais CS aos 20 minutos?",
    "Qual jogador causou mais dano a torres?",
    "Qual campeão foi a primeira escolha do draft?",
]
for p in DEVE_RECUSAR:
    assert dado_ausente(p, "solo") is not None, p

DEVE_PASSAR = [
    "Qual foi a diferença de ouro aos 15 minutos?",       # o competitivo tem gold_diff_at15
    "Qual campeão tem mais dano causado em média?",       # solo tem dmg_to_champions
    "Quais os 5 campeões mais jogados na posição MIDDLE?",
    "Qual equipe teve a maior sequência de vitórias?",    # sequência não é série
    "Qual a duração média das partidas por patch?",
    "Qual liga teve mais jogos profissionais em 2026?",
    "Quantas partidas tiveram mais de 40 eliminações somando as duas equipes?",
]
for p in DEVE_PASSAR:
    assert dado_ausente(p, "solo") is None, p

# dano só é ausente no competitivo; no solo a pergunta segue para o modelo
assert dado_ausente("Qual jogador causou mais dano por partida?", "solo") is None
assert dado_ausente("Qual jogador causou mais dano por partida?", "competitivo") is not None

# a SQL de recusa tem a forma da recusa do modelo e escapa aspas
s = sql_de_recusa("o banco não tem 'x'")
assert s.startswith("SELECT 'não é possível responder:") and "''x''" in s and s.endswith("AS aviso;")
print("OK")
