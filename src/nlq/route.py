"""Roteador da consulta em linguagem natural: solo queue, competitivo ou os dois.

O sistema tem duas bases paralelas com convenções diferentes (ver
docs/plano_roteamento_nlq.md) e uma caixa de pergunta só. Em 50 perguntas livres,
várias foram respondidas sem que o sistema soubesse, nem dissesse, de qual base
falava. Este módulo decide a base ANTES de gerar a SQL, e nunca adivinha em silêncio:
sem pista, a resposta é AMBOS (as duas bases, rotuladas).

Duas camadas:
  1. REGRAS de código, determinísticas e testáveis. As pistas vêm do esquema: uma
     métrica que existe em só uma base roteia para ela (cs, dano, itens e
     banimentos só existem no solo queue; liga, equipe, patch e a diferença de
     ouro aos 15 minutos só no competitivo). Palavras explícitas ("profissional",
     "solo queue") mandam mais que as pistas de vocabulário.
  2. Uma chamada curta ao modelo, só para o resíduo (conflito de pistas ou sem
     pista, onde um nome próprio como "Faker" ou "T1" pode decidir). A saída é
     tratada como DADO: qualquer coisa fora de SOLO/PRO/AMBOS, ou qualquer falha da
     chamada, vira AMBOS. O roteador só escolhe uma dica; a segurança continua toda
     em sql_guard.py.

A continuação de uma conversa herda a base do turno anterior, se a nova pergunta
não trouxer pista nenhuma.

Rótulo de referência dos testes: pela PISTA no texto, não pela intenção de quem
perguntou (a intenção não é recuperável do texto).
"""
import os
import re
import unicodedata

SOLO, PRO, AMBOS = "solo", "competitivo", "ambos"
CLASSES_VALIDAS = {"SOLO": SOLO, "PRO": PRO, "AMBOS": AMBOS}

# --- pistas explícitas de base: mandam mais que as de vocabulário ---------------------
FORTE_PRO = re.compile(r"\b(profission\w+|competitiv\w+|pro play)\b")
FORTE_SOLO = re.compile(r"\b(solo ?queue|soloq|ranquead\w*|ranked|fila solo)\b")

# --- pistas de vocabulário e de dado ---------------------------------------------------
FRACO_PRO = re.compile(
    r"\b(equipes?|ligas?|temporadas?|splits?|playoffs?|patch(?:es)?|torneios?|campeonatos?|"
    r"mundial|msi|worlds|lck|lpl|lec|lta|cblol|lcs|lcl|pcs|vcs)\b"
    r"|\bdiferenc\w* (?:media )?de (?:ouro|xp|cs)\b"
)
FRACO_SOLO = re.compile(
    r"\b(tier|elo|challenger|grandmaster|grao.?mestre|divisao|"
    r"time (?:azul|vermelho)|"
    r"cs|farm|dano|visao|wards?|itens?|build|builds|"
    r"banid\w*|bans?|banimentos?|"
    r"jogadores cadastrados|tabela de jogadores|versao do jogo)\b"
)
# posições no padrão do banco do solo queue (MAIÚSCULAS); testada no texto original
POSICAO_SOLO = re.compile(r"\b(TOP|JUNGLE|MIDDLE|BOTTOM|UTILITY)\b")


def normalizar(texto: str) -> str:
    """minúsculas e sem acento: 'duração' vira 'duracao'."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return sem_acento.lower()


def _pistas(pergunta: str) -> dict[str, list[str]]:
    n = normalizar(pergunta)
    return {
        "forte_pro": [m.group(0) for m in FORTE_PRO.finditer(n)],
        "forte_solo": [m.group(0) for m in FORTE_SOLO.finditer(n)],
        "fraco_pro": [m.group(0) for m in FRACO_PRO.finditer(n)],
        "fraco_solo": [m.group(0) for m in FRACO_SOLO.finditer(n)]
        + [m.group(0) for m in POSICAO_SOLO.finditer(pergunta)],
    }


def classificar_por_regras(pergunta: str) -> tuple[str | None, dict]:
    """(classe, pistas). classe None = as regras não decidem (vai ao resíduo)."""
    p = _pistas(pergunta)
    if p["forte_pro"] and p["forte_solo"]:
        return AMBOS, p  # a própria pergunta cita as duas bases
    if p["forte_pro"]:
        return PRO, p
    if p["forte_solo"]:
        return SOLO, p
    if p["fraco_pro"] and not p["fraco_solo"]:
        return PRO, p
    if p["fraco_solo"] and not p["fraco_pro"]:
        return SOLO, p
    return None, p  # conflito de pistas, ou nenhuma


PROMPT_ROTEADOR = (
    "Você classifica uma pergunta sobre League of Legends. Há duas bases de dados:\n"
    "SOLO: partidas ranqueadas solo queue (times azul e vermelho, sem nome de equipe, "
    "jogadores por puuid, itens, banimentos, CS, dano, elos).\n"
    "PRO: partidas profissionais (equipes e jogadores com nome, ligas como LCK, LPL e "
    "LEC, patches, anos).\n"
    "Responda com UMA palavra: SOLO, PRO ou AMBOS. Somente a palavra, sem explicação.\n"
    "- PRO se a pergunta citar uma equipe, jogador, liga ou torneio profissional "
    "(ex.: T1, Faker, LCK, Worlds), ou algo que só existe no profissional.\n"
    "- SOLO se citar algo que só existe no solo queue (itens, banimentos, elo, CS, dano).\n"
    "- AMBOS se a pergunta puder valer para as duas bases, ou se pedir as duas. "
    "Se não houver pista, responda AMBOS. Nunca adivinhe."
)


def _chamar_modelo(pergunta: str, base_anterior: str | None) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    texto = pergunta if not base_anterior else f"(base do turno anterior: {base_anterior})\n{pergunta}"
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=16,
        temperature=0,
        system=PROMPT_ROTEADOR,
        messages=[{"role": "user", "content": texto}],
    )
    return msg.content[0].text if msg.content else ""


def rotear(pergunta: str, base_anterior: str | None = None, modelo=None) -> dict:
    """Decide a base. Devolve {"classe", "origem", "pistas"}.

    classe: "solo", "competitivo" ou "ambos".
    origem: "regras", "heranca" (continuação sem pista), "modelo" ou "padrao" (saída
    inválida ou falha da chamada, tratada como AMBOS).
    base_anterior: "solo" ou "competitivo" quando o turno anterior foi numa base só.
    modelo: função (pergunta, base_anterior) -> texto, injetável nos testes.
    """
    classe, pistas = classificar_por_regras(pergunta)
    if classe is not None:
        return {"classe": classe, "origem": "regras", "pistas": pistas}
    sem_pista = not any(pistas.values())
    if sem_pista and base_anterior in (SOLO, PRO):
        return {"classe": base_anterior, "origem": "heranca", "pistas": pistas}
    try:
        bruto = (modelo or _chamar_modelo)(pergunta, base_anterior)
    except Exception:  # noqa: BLE001  # falha da chamada não pode derrubar a pergunta: roda as duas bases
        return {"classe": AMBOS, "origem": "padrao", "pistas": pistas}
    # só a PRIMEIRA linha vale: o modelo às vezes responde a palavra e segue explicando
    # (visto ao vivo em 2026-11-04, cortado pelos 16 tokens); o resto é descartado.
    # A linha inteira tem que ser a palavra: "SOLO ou PRO" não é resposta.
    linhas = (bruto or "").strip().splitlines()
    primeira = linhas[0] if linhas else ""
    resposta = CLASSES_VALIDAS.get(re.sub(r"[^A-Za-z]", "", primeira).upper())
    if resposta is None:
        return {"classe": AMBOS, "origem": "padrao", "pistas": pistas}
    return {"classe": resposta, "origem": "modelo", "pistas": pistas}
