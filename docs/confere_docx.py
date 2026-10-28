"""Confere o .docx gerado contra as regras formais do TCC II.

POR QUE UM SCRIPT: o checklist de entrega afirmava "41 títulos, 0 em negrito"
e "12 referências". Os dois foram escritos à mão e envelheceram — o
documento ganhou seções novas (6.1, 6.2) e 6 referências de método. Número
de checklist que ninguém conta é número que mente.

Verifica: contagem de títulos e se estão em negrito (regra invertida em
2026-10-05: o modelo OFICIAL de artigo do Prof. Elvandi, lido do XML,
define negrito+caixa alta no estilo 'heading 1' — isto substitui a leitura
anterior, "maiúscula sem negrito", que vinha de um comentário pontual numa
revisão do TCC I); entradas de REFERÊNCIAS; legendas de figura e de quadro;
tabelas e imagens.

Nomes de estilo: Despite "REFERÊNCIAS" ser o estilo do TCC I, os estilos de
título ficam em inglês no arquivo ('Heading 1'..'Heading 3') porque é o que o
pandoc escreve. A primeira versão deste script procurava "Título 1" e
encontrou zero títulos, zero negrito e "suspiciosamente poucas referências"
— um relatório de conformidade errado é pior do que nenhum.

Uso:
    .venv\\Scripts\\python.exe docs\\confere_docx.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document

DOCX = Path(__file__).resolve().parent.parent / "docs" / "tcc2_final.docx"
RE_TITULO = re.compile(r"Heading\s*\d", re.I)


def main() -> None:
    if not DOCX.exists():
        sys.exit(f"ERRO: {DOCX} nao existe — rode build_tcc_docx.py antes")
    d = Document(str(DOCX))

    titulos, sem_negrito = [], []
    for p in d.paragraphs:
        if not RE_TITULO.match(p.style.name or ""):
            continue
        txt = p.text.strip()
        if not txt:
            continue  # sumário/TOC não conta como título do corpo
        titulos.append(txt)
        # negrito vem do ESTILO (aplicar_negrito_titulos), não de run.bold
        # individual — runs de título normalmente não setam bold explícito,
        # herdam do estilo. Checar o estilo é o jeito certo de verificar.
        if not (p.style.font.bold or any(r.bold for r in p.runs)):
            sem_negrito.append(txt)

    # REFERÊNCIAS: o TCC I traz um estilo dedicado, então basta contar os
    # parágrafos nele — não é preciso inferir entradas por linhas em branco.
    refs = [p for p in d.paragraphs if (p.style.name or "") == "REFERÊNCIAS"]

    leg_fig = [
        p
        for p in d.paragraphs
        if (p.style.name or "") == "Caption" and p.text.strip().upper().startswith("FIGURA")
    ]
    leg_quad = [
        p
        for p in d.paragraphs
        if (p.style.name or "") == "Caption" and p.text.strip().upper().startswith("QUADRO")
    ]
    fontes = [p for p in d.paragraphs if (p.style.name or "") == "Fonte das ilustrações"]

    print(f"títulos de seção        : {len(titulos)}")
    print(f"títulos SEM negrito     : {len(sem_negrito)}  (regra: zero — "
          f"modelo oficial do Prof. Elvandi exige negrito+caixa alta)")
    for t in sem_negrito:
        print(f"   VIOLAÇÃO: {t!r}")
    print(f"entradas de REFERÊNCIAS : {len(refs)}")
    print(f"legendas de Figura      : {len(leg_fig)}")
    print(f"legendas de Quadro      : {len(leg_quad)}")
    print(f"fontes de ilustração    : {len(fontes)}")
    print(f"tabelas                 : {len(d.tables)}")
    print(f"imagens                 : {len(d.inline_shapes)}")

    problemas = []
    if sem_negrito:
        problemas.append(f"{len(sem_negrito)} título(s) de seção SEM negrito")
    if len(titulos) < 40:
        problemas.append(f"suspiciousamente poucos títulos ({len(titulos)})")
    if len(refs) != 32:
        problemas.append(f"referências: esperado 32, achou {len(refs)}")
    # Esperado vem do markdown, não de constante (2026-10-28): com quadros e
    # recortes entrando no corpo, o "6" fixo virou falso. Cada linha
    # "Quadro – Título" é um quadro; cada marcador "Figura – ... | x.png" é
    # uma figura do corpo, e o Apêndice F traz mais 6 telas inteiras.
    import re as _re
    md = (Path(__file__).resolve().parent / "tcc2_texto.md").read_text(encoding="utf-8")
    md = md.split("## Pendências finais")[0]  # log interno, não vai ao .docx
    exp_quad = len(_re.findall(r"(?m)^Quadro\s*[—–-]\s*\S", md))
    exp_fig = len(_re.findall(r"(?m)^Figura\s*[—–-].*\|\s*\S+\.png\s*$", md)) + 6
    if len(leg_fig) != exp_fig:
        problemas.append(f"legendas de figura: esperado {exp_fig}, achou {len(leg_fig)}")
    if len(leg_quad) != exp_quad:
        problemas.append(f"legendas de quadro: esperado {exp_quad}, achou {len(leg_quad)}")
    if len(fontes) != len(leg_fig) + len(leg_quad):
        problemas.append(
            f"fontes ({len(fontes)}) não cobrem as legendas "
            f"({len(leg_fig) + len(leg_quad)})"
        )
    if len(d.tables) != exp_quad:
        problemas.append(f"tabelas: esperado {exp_quad}, achou {len(d.tables)}")
    if len(d.inline_shapes) != exp_fig:
        problemas.append(f"imagens: esperado {exp_fig}, achou {len(d.inline_shapes)}")

    print()
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        sys.exit(1)
    print("VEREDITO: conforme")


if __name__ == "__main__":
    main()