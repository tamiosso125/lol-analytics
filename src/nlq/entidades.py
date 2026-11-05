"""Resolve, no banco, os NOMES citados na pergunta (campeão, liga, equipe, jogador).

Por que existe (2026-11-05): no gabarito automático (203 perguntas), a maior família de falha
foi o modelo "corrigir" o nome e não achar nada: o solo guarda `MonkeyKing`, `LeeSin`,
`MasterYi`, mas ele escrevia 'Monkey King'; tratava a liga HLL ou EWC como equipe, trocava a
liga `LPLOL` por `LPL`, mudava a caixa de `inf`, lia `RED Canids` como lado vermelho e
recusava o campeão novo `Locke` porque "não existe" na memória dele. Regra em texto não
resolveu; aqui o nome exato vem do banco (mesmo princípio de feedback_ground_llm_facts:
fato do domínio sai de tabela, não da memória do modelo).

Como funciona: índice (nome sem caixa, acento nem pontuação -> nome exato e tipo) lido do
banco uma vez. A pergunta é varrida por sequências de 1 a 5 palavras; vale a MAIOR sequência
que casa (então "RED Canids" vence "red"). O resultado vira uma dica ANTES da pergunta, com
o nome literal e o tipo (liga não é equipe). Não gera SQL e não filtra nada sozinho.
"""
import os
import re
import unicodedata

# palavras comuns que não devem ser tomadas por nome de equipe ou jogador
STOP = {
    "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "por", "com", "sem", "para", "um", "uma",
    "qual", "quais", "quanto", "quantos", "quantas", "quantidade", "media", "total", "maior", "menor", "mais",
    "menos", "jogo", "jogos", "partida", "partidas", "time", "times", "equipe", "equipes", "liga", "ligas",
    "jogador", "jogadores", "campeao", "campeoes", "taxa", "vitoria", "vitorias", "derrota", "derrotas", "win",
    "rate", "kda", "patch", "ano", "mes", "dia", "lado", "azul", "vermelho", "red", "blue", "top", "mid", "bot",
    "jng", "sup", "que", "ou", "foi", "sao", "tem", "teve", "ter", "seu", "sua", "pelo", "pela", "entre", "sobre",
    "ate", "aos", "ao", "como", "durante", "numero", "posicao", "banimentos", "banido", "picks", "pick",
    "eliminacoes", "mortes", "assistencias", "dragoes", "baroes", "torres", "ouro", "dano", "visao", "duracao",
    "aproveitamento", "competitivo", "profissional", "profissionais", "solo", "queue", "disputou", "disputadas",
    "disputados", "jogou", "jogado", "faz", "fez", "por", "item", "itens", "compras", "comprado", "posicoes",
}

_INDICE: dict | None = None


def normalizar(texto: str) -> str:
    sem = unicodedata.normalize("NFKD", str(texto))
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in sem if not unicodedata.combining(c)).lower())


def _carregar() -> dict:
    """norm -> lista de (tipo, nome_exato, base). Tipos: campeao, liga, equipe, jogador."""
    import psycopg2

    from src import config  # noqa: F401

    consultas = [
        ("campeao", "solo", "SELECT DISTINCT champion_name FROM participants WHERE champion_name IS NOT NULL"),
        ("campeao", "competitivo", "SELECT DISTINCT champion FROM pro_players WHERE champion IS NOT NULL"),
        ("liga", "competitivo", "SELECT DISTINCT league FROM pro_games WHERE league IS NOT NULL"),
        ("equipe", "competitivo", "SELECT DISTINCT team_name FROM pro_games WHERE team_name IS NOT NULL"),
        ("jogador", "competitivo", "SELECT DISTINCT player_name FROM pro_players WHERE player_name IS NOT NULL"),
    ]
    indice: dict = {}
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        conn.set_session(readonly=True)
        cur = conn.cursor()
        cur.execute("SET statement_timeout = 20000")
        for tipo, base, sql in consultas:
            cur.execute(sql)
            for (nome,) in cur.fetchall():
                n = normalizar(nome)
                if len(n) < 2:
                    continue
                indice.setdefault(n, [])
                if (tipo, nome, base) not in indice[n]:
                    indice[n].append((tipo, nome, base))
    finally:
        conn.close()
    return indice


def indice() -> dict:
    global _INDICE
    if _INDICE is None:
        _INDICE = _carregar()
    return _INDICE


def encontrar(pergunta: str, idx: dict | None = None) -> list[dict]:
    """Entidades citadas: [{trecho, tipo, nome, base}], da maior sequência para a menor."""
    idx = indice() if idx is None else idx
    palavras = re.findall(r"[\w'.\-]+", pergunta)
    usadas = [False] * len(palavras)
    achadas = []
    for tam in range(5, 0, -1):
        for i in range(0, len(palavras) - tam + 1):
            if any(usadas[i:i + tam]):
                continue
            trecho = " ".join(palavras[i:i + tam])
            n = normalizar(trecho)
            if tam == 1:
                if n in STOP:
                    continue
                # duas letras só valem em maiúsculas (AL, EM): "em" minúsculo é preposição
                if len(n) < 3 and not (len(n) == 2 and palavras[i].isupper()):
                    continue
            elif n in STOP:
                continue
            if n not in idx:
                continue
            for tipo, nome, base in idx[n]:
                achadas.append({"trecho": trecho, "tipo": tipo, "nome": nome, "base": base})
            for k in range(i, i + tam):
                usadas[k] = True
    return achadas


COLUNA = {
    ("campeao", "solo"): "participants.champion_name",
    ("campeao", "competitivo"): "pro_players.champion",
    ("liga", "competitivo"): "pro_games.league",
    ("equipe", "competitivo"): "pro_games.team_name",
    ("jogador", "competitivo"): "pro_players.player_name",
}
ROTULO = {"campeao": "campeão", "liga": "LIGA (não é equipe)", "equipe": "EQUIPE (não é liga nem lado)",
          "jogador": "jogador profissional"}


def dica(pergunta: str, base: str | None, idx: dict | None = None) -> str:
    """Texto para o prompt ('' quando nada foi encontrado). Só entidades da `base`."""
    achadas = [a for a in encontrar(pergunta, idx) if base is None or a["base"] == base]
    if not achadas:
        return ""
    linhas = []
    for a in achadas:
        linhas.append(f"- \"{a['trecho']}\" é {ROTULO[a['tipo']]}; grafia EXATA no banco: "
                      f"'{a['nome'].replace(chr(39), chr(39) * 2)}' ({COLUNA[(a['tipo'], a['base'])]})")
    return ("NOMES NO BANCO (resolvidos antes da consulta; use a grafia literal, sem corrigir "
            "espaço, caixa ou pontuação, e não diga que o nome não existe):\n" + "\n".join(linhas))


def so_do_competitivo(pergunta: str, idx: dict | None = None) -> bool:
    """True se a pergunta cita liga, equipe ou jogador profissional e nenhum campeão do solo
    (nomes que só existem no banco competitivo): serve de pista extra ao roteador."""
    achadas = encontrar(pergunta, idx)
    tipos = {a["tipo"] for a in achadas}
    return bool(tipos & {"liga", "equipe", "jogador"})
