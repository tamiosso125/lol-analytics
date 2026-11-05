"""Recusa determinística de perguntas que o banco NÃO consegue responder.

Por que existe (2026-11-05): o esquema já dizia ao modelo, em texto, que o banco não
tem "quem fez algo primeiro", série, dano a torres etc. e para NÃO aproximar. No
segundo conjunto cego (perguntas 101-150) o modelo ignorou a regra em 9 ou 10 de cerca
de 19 perguntas e devolveu um substituto sem rótulo (torres > 0 no lugar de "primeira
torre", um `series_id` inventado...). Regra em prompt é probabilística; esta lista é
determinística e roda ANTES de chamar o modelo. Só barra conceitos que o schema
comprovadamente não tem (conferido em db/schema.sql): na dúvida, deixa passar e o
validador/modelo seguem como antes. A resposta tem o mesmo formato da recusa do modelo
(`SELECT 'não é possível responder: ...' AS aviso`), então a tela e o benchmark a
tratam igual.

Não é regra por pergunta: cada padrão é um conceito (primeiro evento, série, instante
fora dos 15 minutos, dano em estruturas) e vale para qualquer redação.
"""
import re
import unicodedata

SOLO = "solo"
PRO = "competitivo"


def _norm(texto: str) -> str:
    sem = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sem if not unicodedata.combining(c)).lower()


# (padrão sobre o texto normalizado, base em que vale: None = todas, motivo)
_REGRAS: list[tuple[re.Pattern, str | None, str]] = [
    (re.compile(r"\bprimeir[oa]s?\s+(?:sangue|torre|dragao|dragoes|barao|baroes|arauto|arautos|"
                r"abate|abates|eliminacao|eliminacoes|kill|kills|inibidor|objetivo)"),
     None,
     "o banco só tem a contagem total de cada objetivo na partida, não quem fez algo "
     "primeiro nem quando"),
    (re.compile(r"\bprimeira\s+(?:escolha|pick|selecao)\b|\bprimeira\s+fase\s+de\s+ban"),
     None,
     "o banco não registra a ordem do draft nem as fases de banimento (solo: só o "
     "pick_turn de cada banimento; competitivo: nem banimentos)"),
    (re.compile(r"\bseries?\b|\bmelhor\s+de\s+(?:3|5|tres|cinco)\b|\bbo\s?[35]\b"),
     None,
     "o banco não tem identificador de série nem a ordem dos jogos dentro dela"),
    (re.compile(r"\baos?\s+(?:5|10|20|25|30)\s+min"),
     None,
     "o banco não guarda o estado da partida nesse minuto (o competitivo só tem as "
     "diferenças aos 15 minutos; o solo, só totais finais)"),
    (re.compile(r"\bdano\s+(?:a|as|em|nas?|nos?|de)\s+(?:torres?|estruturas?|objetivos?|"
                r"inibidores?|construcoes)"),
     None,
     "o banco não tem dano a estruturas; só o dano total a campeões (participants."
     "dmg_to_champions, solo queue)"),
    (re.compile(r"\bdano\b"),
     PRO,
     "o competitivo (pro_games/pro_players) não tem dano; só kills, deaths e assists"),
    (re.compile(r"\badversario\s+de\s+rota|\boponente\s+de\s+rota|\bcontra\s+(?:seu|o)\s+"
                r"(?:adversario|oponente)\s+direto"),
     PRO,
     "as diferenças aos 15 minutos do competitivo são da EQUIPE, não do jogador contra o "
     "adversário de rota"),
]


def dado_ausente(pergunta: str, base: str | None = None) -> str | None:
    """Motivo (curto) se a pergunta pede algo que o banco não tem; None se pode seguir."""
    texto = _norm(pergunta)
    for padrao, so_na_base, motivo in _REGRAS:
        if so_na_base and base != so_na_base:
            continue
        if padrao.search(texto):
            return motivo
    return None


def sql_de_recusa(motivo: str) -> str:
    """Mesma forma da recusa que o modelo gera, para a tela e o benchmark."""
    return "SELECT 'não é possível responder: " + motivo.replace("'", "''") + "' AS aviso;"
