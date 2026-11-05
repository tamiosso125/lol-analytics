"""Testes do roteador solo queue × competitivo (src/nlq/route.py).

Sem banco e sem API: a chamada ao modelo é substituída por uma função falsa. Rótulo
de referência: a PISTA no texto, não a intenção de quem perguntou.

Grupos:
  * decididas pelas regras (e o modelo NÃO pode ser chamado);
  * residuais (sem pista ou com conflito): o modelo é chamado e a saída é validada;
  * herança na continuação da conversa;
  * robustez: saída malformada e falha da chamada viram AMBOS.

Uso:  .venv\\Scripts\\python.exe tests\\test_route.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.nlq.route import AMBOS, PRO, SOLO, rotear  # noqa: E402

# (pergunta, classe esperada) — todas decididas pelas regras
POR_REGRAS = [
    # --- benchmark de 26 perguntas ---
    ("Qual o win rate do time azul?", SOLO),
    ("Quantas partidas o time vermelho venceu?", SOLO),
    ("Qual a média de ouro (gold_earned) dos jogadores na posição JUNGLE?", SOLO),
    ("Quais os 5 campeões mais jogados na posição MIDDLE?", SOLO),
    ("Qual a média de dano causado a campeões pelos jogadores do time azul?", SOLO),
    ("Quantos jogadores estão no tier Challenger?", SOLO),
    ("Qual o CS (farm) médio dos jogadores na posição TOP?", SOLO),
    ("Qual o campeão com maior win rate entre os jogadores do tier Grandmaster, com pelo menos 10 partidas?", SOLO),
    ("Quantos jogadores estão cadastrados na tabela de jogadores?", SOLO),
    ("Quantas partidas existem por versão do jogo, da mais para a menos frequente?", SOLO),
    ("Quantos jogos profissionais de 2026 existem no banco?", PRO),
    ("Qual o win rate do lado azul no competitivo em 2026?", PRO),
    ("Quais os 5 campeões mais jogados no competitivo em 2026?", PRO),
    ("Qual liga teve mais jogos profissionais em 2026?", PRO),
    # --- perguntas livres ---
    ("Qual equipe venceu mais partidas em 2026?", PRO),
    ("Quais foram as 5 ligas com maior duração média de partida?", PRO),
    ("Como a duração média das partidas variou entre os diferentes patches de 2026?", PRO),
    ("Qual equipe apresentou a maior diferença média de ouro aos 15 minutos?", PRO),
    ("Qual foi a duração média das partidas profissionais em 2026?", PRO),
    ("Quais campeões foram mais banidos em 2026?", SOLO),
    ("Qual foi o campeão mais utilizado na posição UTILITY?", SOLO),
    ("Quais itens a Camille mais constrói?", SOLO),
    # --- a palavra explícita manda mais que a pista de vocabulário ---
    ("Qual o win rate do time azul no profissional?", PRO),
    ("Quantos pontos de liga tem o jogador no solo queue?", SOLO),
    ("Quais equipes têm mais vitórias na fila ranqueada?", SOLO),
    # --- a pergunta cita as duas bases ---
    ("Compare o viés de lado no solo queue e no profissional", AMBOS),
    ("Qual lado vence mais, no ranqueado e no competitivo?", AMBOS),
    # --- acentos e caixa ---
    ("QUAL LIGA TEVE MAIS JOGOS?", PRO),
    ("Qual a duração média das partidas profissionais?", PRO),
]

# sem pista, ou pistas dos dois lados: vão ao modelo
RESIDUAIS = [
    "Quantas partidas existem no banco?",
    "Quais os 5 campeões mais jogados?",
    "Qual a duração média das partidas em minutos?",
    "Qual lado do mapa apresentou a maior taxa de vitória?",
    "Qual foi a partida mais longa registrada em 2026?",
    "Qual jogador teve o maior número de partidas disputadas em 2026?",
    "Qual a equipe com mais bans de campeão?",  # equipe (pro) + bans (solo): conflito
    "Qual liga tem mais itens finalizados?",  # liga (pro) + itens (solo): conflito
]


def modelo_que_responde(texto):
    chamadas = []

    def f(pergunta, base_anterior):
        chamadas.append((pergunta, base_anterior))
        return texto

    f.chamadas = chamadas
    return f


def main() -> int:
    falhas = []

    for pergunta, esperado in POR_REGRAS:
        m = modelo_que_responde("SOLO")
        r = rotear(pergunta, modelo=m)
        if r["classe"] != esperado:
            falhas.append(f"REGRAS: {pergunta!r} -> {r['classe']} (esperado {esperado}) pistas={r['pistas']}")
        if r["origem"] != "regras":
            falhas.append(f"REGRAS: {pergunta!r} devia vir das regras, veio de {r['origem']}")
        if m.chamadas:
            falhas.append(f"REGRAS: {pergunta!r} chamou o modelo e não devia")

    for pergunta in RESIDUAIS:
        m = modelo_que_responde("AMBOS")
        r = rotear(pergunta, modelo=m)
        if len(m.chamadas) != 1:
            falhas.append(f"RESIDUAL: {pergunta!r} devia chamar o modelo uma vez e chamou {len(m.chamadas)}")
        if r["classe"] != AMBOS or r["origem"] != "modelo":
            falhas.append(f"RESIDUAL: {pergunta!r} -> {r['classe']}/{r['origem']}")

    # o modelo pode decidir quando há nome próprio
    r = rotear("Quantas partidas o Faker jogou em 2026?", modelo=modelo_que_responde("PRO"))
    if (r["classe"], r["origem"]) != (PRO, "modelo"):
        falhas.append(f"MODELO: Faker devia ir a PRO pelo modelo, foi {r}")

    # herança na continuação
    m = modelo_que_responde("AMBOS")
    r = rotear("e agora só de 2025?", base_anterior=PRO, modelo=m)
    if (r["classe"], r["origem"]) != (PRO, "heranca") or m.chamadas:
        falhas.append(f"HERANCA: devia herdar PRO sem chamar o modelo, foi {r} e {len(m.chamadas)} chamadas")
    r = rotear("e agora só de 2025?", base_anterior=AMBOS, modelo=modelo_que_responde("AMBOS"))
    if r["origem"] != "modelo":
        falhas.append("HERANCA: turno anterior AMBOS não pode herdar")
    r = rotear("e as ligas?", base_anterior=SOLO, modelo=modelo_que_responde("AMBOS"))
    if r["classe"] != PRO or r["origem"] != "regras":
        falhas.append(f"HERANCA: pista nova (liga) deve vencer a herança, foi {r}")

    # robustez: saída que não é SOLO/PRO/AMBOS, falha da chamada
    for ruim in ("talvez", "SOLO ou PRO", "", "Solo queue, com certeza.", "42"):
        r = rotear("Quantas partidas existem?", modelo=modelo_que_responde(ruim))
        if (r["classe"], r["origem"]) != (AMBOS, "padrao"):
            falhas.append(f"ROBUSTEZ: saída {ruim!r} devia virar AMBOS/padrao, foi {r}")
    for ok, esperado in (
        ("solo", SOLO),
        (" pro. ", PRO),
        ("Ambos\n", AMBOS),
        # o modelo responde a palavra e segue explicando (caso real, cortado pelos 16 tokens)
        ("AMBOS\n\nA pergunta é genérica e não especifica se", AMBOS),
        ("PRO\nporque cita uma liga", PRO),
    ):
        r = rotear("Quantas partidas existem?", modelo=modelo_que_responde(ok))
        if r["classe"] != esperado:
            falhas.append(f"ROBUSTEZ: saída {ok!r} devia dar {esperado}, deu {r['classe']}")

    def explode(pergunta, base_anterior):
        raise RuntimeError("API fora do ar")

    r = rotear("Quantas partidas existem?", modelo=explode)
    if (r["classe"], r["origem"]) != (AMBOS, "padrao"):
        falhas.append(f"ROBUSTEZ: falha da chamada devia virar AMBOS/padrao, foi {r}")

    print(f"{len(POR_REGRAS)} por regras, {len(RESIDUAIS)} residuais, mais herança e robustez")
    for f in falhas:
        print("  FALHA:", f)
    print("OK" if not falhas else f"{len(falhas)} FALHA(S)")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
