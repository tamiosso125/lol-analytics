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
    # 2026-11-23: o piso fixo de 40 títulos caiu junto com os 7 apêndices cortados na
    # simplificação do TCC. O esperado agora vem do markdown (todo "##"/"###" antes das
    # pendências, menos o RESUMO, que não é Heading no .docx) e a ESTRUTURA do modelo da
    # banca é conferida pela ordem dos títulos de primeiro nível.
    import re as _r0
    _md0 = (Path(__file__).resolve().parent / "tcc2_texto.md").read_text(encoding="utf-8")
    _md0 = _md0.split("## Pendências finais")[0]
    _tit_md = [l for l in _md0.splitlines() if _r0.match(r"^#{2,3} ", l)]
    _tit_md = [l for l in _tit_md if not l.startswith("## RESUMO")]
    if len(titulos) != len(_tit_md):
        problemas.append(f"títulos: o markdown tem {len(_tit_md)} e o .docx {len(titulos)}")
    _ordem = ["INTRODUÇÃO", "FUNDAMENTAÇÃO TEÓRICA", "TRABALHOS RELACIONADOS", "METODOLOGIA",
              "RESULTADOS E ANÁLISE", "CONCLUSÃO", "REFERÊNCIAS", "APÊNDICE"]
    _h1 = [p.text.strip() for p in d.paragraphs
           if (p.style.name or "").lower().startswith("heading 1") and p.text.strip()]
    _vistos = []
    for t in _h1:
        for nome in _ordem:
            if nome in t.upper():
                _vistos.append(nome)
                break
    # sem repetição de apêndice na checagem de ordem: só o primeiro conta
    _comp = []
    for n in _vistos:
        if not (_comp and _comp[-1] == n):
            _comp.append(n)
    if _comp != _ordem:
        problemas.append(f"estrutura do modelo da banca fora de ordem: {_comp}")
    else:
        print("estrutura (modelo da banca) : " + " > ".join(_ordem))
    # 30 desde 2026-11-23 (Hornik saiu na simplificação); 31 desde 2026-11-03: Yin (2018) saiu quando a leitura do livro mostrou
    # que o trabalho não é estudo de caso no sentido dele
    if len(refs) != 30:
        problemas.append(f"referências: esperado 30, achou {len(refs)}")
    # Esperado vem do markdown, não de constante (2026-10-28): com quadros e
    # recortes entrando no corpo, o "6" fixo virou falso. Cada linha
    # "Quadro – Título" é um quadro; cada marcador "Figura – ... | x.png" é
    # uma figura do corpo, e, se existir o apêndice de telas completas, mais 6 telas inteiras.
    import re as _re
    md = (Path(__file__).resolve().parent / "tcc2_texto.md").read_text(encoding="utf-8")
    md = md.split("## Pendências finais")[0]  # log interno, não vai ao .docx
    exp_quad = len(_re.findall(r"(?m)^Quadro\s*[—–-]\s*\S", md))
    exp_fig = len(_re.findall(r"(?m)^Figura\s*[—–-].*\|\s*\S+\.png\s*$", md)) + (
        6 if "Telas completas da plataforma" in md else 0)  # 2026-11-23: Apêndice de telas cortado
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

    # 2026-11-23: as notas de rodapé 1 (aluno), 2 (orientador) e 3 (aviso da Riot) têm de
    # estar nos parágrafos certos, cada chamada com sua nota e a marca no mesmo run da
    # chamada (formato do próprio Word). Com a marca num run separado, o Word deslocava
    # as chamadas 1 e 2 um parágrafo adiante e apagava a 3 ao regravar o arquivo, e outros
    # leitores mostravam "1*" e uma marca "1" sem nota.
    import re as _r1
    import zipfile as _zf
    _z = _zf.ZipFile(str(DOCX))
    _fn = _z.read("word/footnotes.xml").decode("utf8")
    _xml = _z.read("word/document.xml").decode("utf8")
    _ids_nota = sorted(int(i) for i in _r1.findall(r'<w:footnote [^>]*w:id="(\d+)"', _fn) if int(i) > 0)
    _ids_ref = sorted(int(i) for i in _r1.findall(r'<w:footnoteReference[^>]*w:id="(\d+)"', _xml))
    if _ids_nota != _ids_ref:
        problemas.append(f"notas de rodapé: chamadas {_ids_ref} e textos {_ids_nota} não casam")
    _ancora = {}
    for p in d.paragraphs:
        for fid in _r1.findall(r'<w:footnoteReference[^>]*w:id="(\d+)"', p._p.xml):
            _ancora[int(fid)] = p.text.strip()
    if not _ancora.get(1, "").startswith("Guilherme") or not _ancora.get(2, "").startswith("Elvandi"):
        problemas.append(f"notas de rodapé 1 e 2 fora dos nomes do aluno e do orientador: "
                         f"{ {k: v[:25] for k, v in _ancora.items()} }")
    _sem_marca_no_run = _r1.findall(r'<w:footnoteReference[^>]*/></w:r>', _xml)
    if _sem_marca_no_run:
        problemas.append(f"{len(_sem_marca_no_run)} chamada(s) de nota sem a marca no mesmo run")
    if not problemas:
        print(f"notas de rodapé              : chamadas {_ids_ref} ancoradas, cada uma com seu texto")
    # texto alternativo nas figuras
    _sem_alt = [i for i, s in enumerate(d.inline_shapes, 1) if not s._inline.docPr.get("descr")]
    if _sem_alt:
        problemas.append(f"figuras sem texto alternativo: {_sem_alt}")

    print()
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        sys.exit(1)
    print("VEREDITO: conforme")


if __name__ == "__main__":
    main()