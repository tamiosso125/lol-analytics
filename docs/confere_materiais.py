"""Confere os materiais derivados do TCC contra os valores que o texto já trocou.

POR QUE EXISTE: `verifica_tcc.py` só lê `docs/tcc2_texto.md`. Depois da
correção do vazamento do quadro final (2026-11-08), o texto foi refeito e
passou, mas o README, o `handoff.md` e o guia da banca continuaram com
0,7636 / 0,8490 / 40.816, e o guia ainda dizia que a divisão cronológica
"nunca fica abaixo" da aleatória, o que deixou de ser verdade. O pptx da
defesa só foi conferido porque alguém lembrou de rodar um grep à mão. Esses
são exatamente os materiais que a banca compara com a fala.

O QUE CONFERE, em cada material:
  1. nenhum valor de `VALORES_SUBSTITUIDOS` ou `VALORES_PRE_VAZAMENTO`
     (importados de `verifica_tcc.py`, fonte única) nem forma de
     `PADROES_REFUTADOS`, A MENOS QUE a ocorrência seja citação histórica;
  2. os números principais de hoje presentes, onde o material deve tê-los.

CITAÇÃO HISTÓRICA: diferente do texto do TCC, o guia e as notas do pptx
explicam o que mudou ("antes da correção eram 0,0927"). A ocorrência é aceita
quando, a até `JANELA` caracteres, aparece um marcador de passado (`→`,
"antes", "era/eram", "antiga", "não use", "não mais", "vazamento", "na base da
época"). LIMITE CONHECIDO: um número velho de verdade, escrito perto de um
desses marcadores por acaso, passa. A janela é curta para isso ser raro, e o
segundo teste (número novo presente) cobre o caso mais comum, o de trocar só
parte dos números.

O site de estudo e o deck são artefatos publicados no claude.ai e não estão
no repositório; passe as cópias locais como argumento.

Uso:
    .venv\\Scripts\\python.exe docs\\confere_materiais.py
    .venv\\Scripts\\python.exe docs\\confere_materiais.py <estudo.html> <pasta-do-deck>
Exit code 0 = nenhum resíduo.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "docs"))
import verifica_tcc as v  # noqa: E402  (fonte única das listas)

JANELA = 120
MARCADOR_HISTORICO = re.compile(
    r"→|\bantes\b|\bera\b|\beram\b|\bantig|n[ãa]o use|n[ãa]o mais|vazamento|"
    r"na base da [ée]poca|passou de|afirmava|hist[óo]ric",
    re.I,
)
# Ocorrência legítima sem marcador por perto: (arquivo, valor, trecho que
# tem de estar na janela, motivo). Explícita e com motivo, para a exceção não
# virar um filtro que ninguém revisa.
EXCECOES: list[tuple[str, str, str, str]] = [
    ("docs/handoff.md", "33.713", "em 2026-10-03",
     "cronologia da coleta: tamanho da base naquela data"),
]

# Os números que cada material tem de citar HOJE (artefatos em reports/:
# metricas_corte, curva_aprendizado, shap_importance_phases, nlq).
PRINCIPAIS_DEFESA = ("0,7641", "0,8487", "40.778", "25.098", "0,0429", "89,2%")
ALVOS: list[tuple[str, tuple[str, ...]]] = [
    ("docs/guia_banca.md", PRINCIPAIS_DEFESA),
    ("docs/bellestraiko_defesa_v4.pptx", ("0,7641", "0,8487", "25.098", "0,0429", "89,2%")),
    ("README.md", ("0,7641", "0,8487")),
    ("docs/handoff.md", ("40.778", "0,8487")),
    ("docs/scripts.md", ()),
    ("docs/comandos.md", ()),
]
# Telas: o texto de "Leitura" de cada página também é material que a banca vê.
ALVOS += [(str(p.relative_to(RAIZ)).replace("\\", "/"), ())
          for p in sorted((RAIZ / "frontend" / "src" / "pages").glob("*.tsx"))
          if ".test." not in p.name]
PRINCIPAIS_EXTRA = ("0,7641", "0,8487", "0,0429")
SUFIXOS_TEXTO = {".html", ".htm", ".md", ".js", ".jsx", ".ts", ".tsx", ".json", ".txt"}

FALHAS: list[str] = []


def _texto_pptx(caminho: Path) -> list[tuple[str, str]]:
    """Texto de cada slide e de cada nota. As tags saem sem espaço porque o
    PowerPoint quebra um número em vários <a:t> ("0,76" + "41")."""
    partes = []
    with zipfile.ZipFile(caminho) as z:
        for nome in sorted(z.namelist()):
            if re.match(r"ppt/(slides/slide|notesSlides/notesSlide)\d+\.xml$", nome):
                xml = z.read(nome).decode("utf-8")
                partes.append((nome, re.sub(r"<[^>]+>", "", xml)))
    return partes


def _textos(caminho: Path) -> list[tuple[str, str]]:
    if caminho.suffix.lower() == ".pptx":
        return _texto_pptx(caminho)
    if caminho.is_dir():
        return [(str(p), p.read_text(encoding="utf-8", errors="replace"))
                for p in sorted(caminho.rglob("*"))
                if p.is_file() and p.suffix.lower() in SUFIXOS_TEXTO]
    return [(str(caminho), caminho.read_text(encoding="utf-8", errors="replace"))]


def conferir(rotulo: str, caminho: Path, principais: tuple[str, ...]) -> None:
    if not caminho.exists():
        FALHAS.append(f"{rotulo}: não existe")
        return
    partes = _textos(caminho)
    proibidos = v.VALORES_SUBSTITUIDOS + v.VALORES_PRE_VAZAMENTO
    achados = 0
    for nome, texto in partes:
        local = Path(nome).name
        for valor, porque in proibidos:
            for m in re.finditer(re.escape(valor), texto):
                janela = texto[max(0, m.start() - JANELA): m.end() + JANELA]
                if MARCADOR_HISTORICO.search(janela):
                    continue
                # `0,7573` entre crases é o NOME do valor (a documentação da
                # própria lista em scripts.md), não uma afirmação sobre o modelo
                if texto[m.start() - 1: m.start()] == "`" and texto[m.end(): m.end() + 1] == "`":
                    continue
                if any(rotulo == arq and valor == val and trecho in janela
                       for arq, val, trecho, _ in EXCECOES):
                    continue
                linha = texto[: m.start()].count("\n") + 1
                trecho = re.sub(r"\s+", " ", texto[max(0, m.start() - 50): m.end() + 40]).strip()
                FALHAS.append(f"{rotulo} [{local}:{linha}] {valor} ({porque}) -> {trecho!r}")
                achados += 1
        for padrao, porque in v.PADROES_REFUTADOS:
            for m in re.finditer(padrao, texto, re.I):
                if MARCADOR_HISTORICO.search(texto[max(0, m.start() - JANELA): m.end() + JANELA]):
                    continue
                linha = texto[: m.start()].count("\n") + 1
                FALHAS.append(f"{rotulo} [{local}:{linha}] {porque}")
                achados += 1
    tudo = "\n".join(t for _, t in partes)
    faltam = [n for n in principais if n not in tudo]
    for n in faltam:
        FALHAS.append(f"{rotulo}: número principal de hoje ausente: {n}")
    estado = "ok" if not achados and not faltam else "FALHA"
    print(f"  {estado:5} {rotulo} ({len(partes)} parte(s), {len(principais)} número(s) exigido(s))")


def main() -> None:
    print("Materiais derivados do TCC x valores substituídos")
    for rel, principais in ALVOS:
        conferir(rel, RAIZ / rel, principais)
    for extra in sys.argv[1:]:
        conferir(Path(extra).name, Path(extra), PRINCIPAIS_EXTRA)
    if len(sys.argv) == 1:
        print("  (site de estudo e deck não conferidos: passe as cópias locais como argumento)")
    print()
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S):")
        for f in FALHAS:
            print(f"  - {f}")
        print("VEREDITO: há resíduo")
        sys.exit(1)
    print("VEREDITO: sem resíduo")


if __name__ == "__main__":
    main()
