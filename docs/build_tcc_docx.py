"""Gera o .docx do TCC II a partir de `tcc2_texto.md`, no padrao do modelo
institucional da UNISINOS.

POR QUE DOCX E NAO LATEX: o modelo que a coordenacao distribui foi produzido em
Microsoft Word (o PDF oficial de 2026-09-28 tem `/Producer: Microsoft Word`).
A classe `UNISINOSartigo.cls` do pacote tugunisinos tambem existe e funciona,
mas e um projeto comunitario - usar o proprio TCC 1 como documento de
referencia de estilo mantem margens, fonte e espacamento identicos ao que a
instituicao ja aprovou.

Como funciona (3 etapas):
  1. preprocessa o Markdown: remove cabecalho de trabalho, bloco de
     pendencias internas e a secao "Pendencias finais antes da entrega";
  2. pandoc gera o corpo do .docx com `--reference-doc` = TCC 1, para herdar
     margens/fonte/espacamento de base (ja aprovados pela instituicao);
  3. python-docx monta capa e folha de rosto (que o pandoc nao faz) e
     resumo/abstract, comeca a numeracao de paginas no corpo (SEM sumario
     nem lista de ilustracoes/quadros — nenhum dos 10 TCC II aprovados
     usados como referencia tem qualquer um dos tres, confirmado em
     2026-10-05), e sobrescreve os 2 detalhes onde o TCC 1 diverge do
     modelo OFICIAL de artigo do
     Prof. Elvandi (`ajustar_tipografia`: recuo 1,25cm; `aplicar_negrito_
     titulos`: titulos em negrito+caixa alta) — ver os docstrings de cada
     funcao para a medicao exata (2026-10-05, XML do .doc convertido via
     automacao do Word).

Uso:  .venv\\Scripts\\python.exe docs\\build_tcc_docx.py
Depende de pandoc no PATH (winget install JohnMacFarlane.Pandoc).
"""
import os
import re
import subprocess
import sys

import docx
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from lxml import etree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "docs", "tcc2_texto.md")
OUT = os.path.join(ROOT, "docs", "tcc2_final.docx")
STAGE = os.path.join(ROOT, "docs", ".build_tcc_stage.md")

# Identidade e metadados extraidos do TCC 1 (TCC_Final.docx, aprovado) e do
# modelo oficial da UNISINOS de 2026-09-28. NAO sao inventados: o nome, o curso,
# a cidade, o ano, o orientador e o formato de capa/folha foram lidos dos
# arquivos citados.
ALUNO = "GUILHERME RIBEIRO LEMOS TAMIOSSO"
ALUNO_NOME_PROPRIO = "Guilherme Ribeiro Lemos Tamiosso"
CURSO = "GRADUAÇÃO EM CIÊNCIA DA COMPUTAÇÃO"
UNIVERSIDADE = "UNIVERSIDADE DO VALE DO RIO DOS SINOS (UNISINOS)"
ORIENTADOR = "Orientador: Prof. Dr. Elvandi da Silva Júnior"
ORIENTADOR_NOME_PROPRIO = "Elvandi da Silva Júnior"
LOCAL_ANO = ("Porto Alegre", "2026")

# Rodapé de autor/orientador no título do artigo (Bloco D da revisão,
# 2026-10-05): elemento presente nos 10 TCC II aprovados e no .doc oficial
# do Prof. Elvandi, ausente até aqui no nosso .docx. E-mail institucional
# do aluno fornecido pelo usuário (2026-10-05) — não é inventado; o do
# orientador é o mesmo em TODOS os 10 aprovados (verificado, não suposto).
NOTA_ALUNO = (
    "Graduando em Ciência da Computação na Universidade do Vale do Rio "
    "dos Sinos (UNISINOS). E-mail: Gtamiosso@edu.unisinos.br."
)
NOTA_ORIENTADOR = (
    "Orientador, Professor Dr. da Escola Politécnica da UNISINOS. "
    "E-mail: elvandi@unisinos.br."
)
TITULO_PT = (
    "PLATAFORMA INTELIGENTE PARA ANÁLISE DE DADOS DE ESPORTS: "
    "Uma proposta para League of Legends com uso de machine learning "
    "e interface em linguagem natural"
)
# O modelo oficial pede "TÍTULO EM PORTUGUÊS" e "TÍTULO EM OUTRO IDIOMA" como
# campos separados na folha de rosto.
TITULO_EN = (
    "INTELLIGENT PLATFORM FOR ESPORTS DATA ANALYSIS: "
    "A proposal for League of Legends using machine learning "
    "and a natural language interface"
)

# Seções que NÃO são numeradas, mesmo sendo "##" no markdown. Sem isto elas
# herdariam a numeração de capítulo junto com INTRODUÇÃO/RESULTADOS/etc.
_RE_NAO_NUMERAR = re.compile(
    r"^## (REFERÊNCIAS|APÊNDICE|ANEXO)", re.M
)

# Títulos dos Quadros, na ordem em que aparecem no documento. A numeração é
# automática (campo SEQ), não texto fixo: assim o Word reenumera se um quadro
# for inserido ou removido, e a "Lista de Quadros" do pre-textual consegue
# listar os quatro.
QUADROS = [
    "Vitória do time vermelho por região",
    "Comparação entre modelos (corte de 15 minutos)",
    "Esquema relacional do banco de dados",
    "Benchmark de 26 perguntas de referência (NLQ)",
    # A 4ª tabela (Apêndice C) não tem título no markdown — só uma nota de
    # método, o que viola a regra da instituição (tabela sem legenda).
    # Título escrito na conversão e CONFIRMADO pelo autor em 2026-10-03.
    "Métricas completas por corte temporal — comparação entre os três modelos",
    "Experimentos negativos de enriquecimento de features",
]

# As 6 capturas do Anexo A. Descrições copiadas da tabela de arquivos que o
# próprio markdown traz — não reescritas.
FIGURAS = [
    ("01_inicio.png", "Página inicial — busca unificada e rankings"),
    ("02_dashboard.png", "Dashboard — KPIs, viés de lado por região e cobertura do dataset"),
    ("03_campeoes.png", "Campeões"),
    ("04_partida_detalhe.png", "Partidas — análise de uma partida individual"),
    ("05_competitivo.png", "Competitivo — solo queue × profissional"),
    ("06_simulador.png", "Simulador — Composição, Estado e Explicabilidade"),
]
FONTE_IMAGENS = (
    "Fonte: Elaborado pelo autor (2026). Capturas de tela geradas via Playwright "
    "(Chromium, largura de 1440 px, altura ajustada à página, sem captura de "
    "página inteira, tema escuro — maior contraste contra o fundo branco da "
    "página impressa) contra a API e o frontend locais."
)
FONTE_QUADROS = "Fonte: Elaborado pelo autor (2026)."

# Secoes internas do rascunho que nao entram no documento final.
_RE_TITULO_TRABALHO = re.compile(r"^# TCC II.*$", re.M)
_RE_PENDENCIAS_FINAIS = re.compile(
    r"^## Pendências finais antes da entrega.*?(?=^## |\Z)", re.M | re.S
)
# O bloco "> Documento de trabalho..." com as pendencias de TCC 1 -> TCC 2.
_RE_BLOCO_TRABALHO = re.compile(r"^>.*?(?=^## RESUMO)", re.M | re.S)
# A secao RESUMO vira o bloco de pre-textual (Resumo/Palavras-chave/Abstract/
# Key-words), montado no passo 3 - nao pode virar um heading do corpo, e as
# linhas de Palavras-chave/Abstract/Key-words tambem sao consumidas aqui
# (senao duplicam no corpo, ja que o passo 3 as reconstroi no pre-textual).
_RE_SECAO_RESUMO = re.compile(
    r"^## RESUMO.*?^\*\*Key-words:\*\*.*?$\n*?^---", re.M | re.S
)


def preprocessar() -> str:
    """Limpa o rascunho e devolve o markdown pronto para o pandoc."""
    with open(MD, encoding="utf-8") as f:
        txt = f.read()
    txt = _RE_BLOCO_TRABALHO.sub("", txt)
    txt = _RE_TITULO_TRABALHO.sub("", txt)
    txt = _RE_PENDENCIAS_FINAIS.sub("", txt)
    # RESUMO inteiro (ate Palavras-chave) sai do corpo; o texto volta no
    # pre-textual porque o modelo pede "Resumo:" como paragrafo, nao secao.
    txt = _RE_SECAO_RESUMO.sub("", txt)
    txt = re.sub(r"^\n{3,}", "\n\n", txt)
    # "---" é separador de seção no rascunho; no .docx viraria régua
    # horizontal visível entre seções, que não existe em documento ABNT
    # (virou 13 InlineShapes do tipo "horizontal line" na primeira geração).
    txt = re.sub(r"^---\s*$", "", txt, flags=re.M)
    return txt.lstrip("\n")


def rodar_pandoc(md: str, reference: str) -> None:
    cmd = [
        "pandoc", md,
        "--from=markdown+pipe_tables+raw_html",
        "--to=docx",
        f"--reference-doc={reference}",
        "--toc-depth=3",
        # NÃO usar --toc: o SUMÁRIO é montado à mão no passo 3, para que o
        # pre-textual (capa/folha/resumo) fique na ordem do modelo e o campo
        # TOC caia depois dele. Com --toc o pandoc gerava um segundo sumário,
        # no topo do corpo, e o documento ficava com dois.
        # NÃO usar --number-sections: o markdown já traz a numeração no
        # próprio texto ("## 1 INTRODUÇÃO", "### 1.1 Tema"). Com a flag, o
        # pandoc acrescentava a dele e saía "1  1 INTRODUÇÃO" — e, pior,
        # REFERÊNCIAS/APÊNDICES/AÑEXOS viravam seções numeradas 7..13.
        # O --shift sobe um nível porque no markdown a seção de 1º grau é
        # "##" (o "#" do título do rascunho foi removido), e o Heading 1 do
        # TCC 1 é o nível de seção, não de título.
        "--shift-heading-level-by=-1",
        "-o", STAGE,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"pandoc falhou:\n{r.stderr}")


def _p(doc, texto="", *, bold=False, align=None, size=12, space_after=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    if space_after is not None:
        pf.space_after = Pt(space_after)
    if texto:
        r = p.add_run(texto)
        r.font.name = "Arial"
        r.font.size = Pt(size)
        r.font.bold = bold
        # east-asian font, senao o Word pode substituir a fonte
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    return p


def _ref_rodape(paragrafo, footnote_id: int) -> None:
    """Insere a marca de chamada de rodapé real (w:footnoteReference),
    sobrescrita em superscrito — não um "*" literal, para o Word numerar/
    renumerar sozinho se a ordem mudar."""
    r = paragrafo.add_run()
    rpr = OxmlElement("w:rPr")
    rstyle = OxmlElement("w:rStyle")
    rstyle.set(qn("w:val"), "Refdenotaderodap")
    rpr.append(rstyle)
    r._r.append(rpr)
    ref = OxmlElement("w:footnoteReference")
    ref.set(qn("w:id"), str(footnote_id))
    r._r.append(ref)


def _adicionar_rodapes(doc, notas: dict[int, str]) -> None:
    """Grava o TEXTO dos rodapés em word/footnotes.xml (a chamada no corpo
    é inserida por `_ref_rodape`, separadamente — os dois lados do rodapé
    moram em partes XML diferentes do .docx).

    `python-docx` 1.2.0 não tem API de alto nível pra rodapé (só pra nota
    de fim é que não existe NENHUMA); a parte já existe no documento
    (herdada do --reference-doc, com os ids -1/0 de separador padrão do
    Word) — só falta ACRESCENTAR os `<w:footnote>` reais. `Part.blob` é
    somente-leitura por fora (expõe só o getter); `_blob` é o atributo que
    o `save()` de fato serializa, e é assim que o python-docx grava
    qualquer parte sem wrapper dedicado (confirmado lendo o fonte de
    `docx.opc.part.Part`).
    """
    rel = next(r for r in doc.part.rels.values() if r.reltype.endswith("footnotes"))
    part = rel.target_part
    raiz = etree.fromstring(part.blob)
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    for fid, texto in notas.items():
        fn = etree.SubElement(raiz, f"{ns}footnote")
        fn.set(f"{ns}id", str(fid))
        p = etree.SubElement(fn, f"{ns}p")
        pPr = etree.SubElement(p, f"{ns}pPr")
        pStyle = etree.SubElement(pPr, f"{ns}pStyle")
        pStyle.set(f"{ns}val", "Textodenotaderodap")
        r1 = etree.SubElement(p, f"{ns}r")
        rPr1 = etree.SubElement(r1, f"{ns}rPr")
        rStyle = etree.SubElement(rPr1, f"{ns}rStyle")
        rStyle.set(f"{ns}val", "Refdenotaderodap")
        etree.SubElement(r1, f"{ns}footnoteRef")
        r2 = etree.SubElement(p, f"{ns}r")
        t = etree.SubElement(r2, f"{ns}t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = " " + texto
    part._blob = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8", standalone=True)


def _campo(paragrafo, instrucao: str) -> None:
    """Insere um campo do Word (SUMARIO, PAGE, ...) que o Word atualiza."""
    r1 = paragrafo.add_run()
    fld = OxmlElement("w:fldChar")
    fld.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instrucao
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    r1._r.append(fld)
    r1._r.append(instr)
    r1._r.append(fld2)
    r2 = paragrafo.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    r2._r.append(end)


def _numeracao_comeca_em_um(doc) -> None:
    """Zera a contagem no inicio do corpo: a capa e a folha nao contam."""
    for sec in doc.sections:
        sectPr = sec._sectPr
        pgNum = sectPr.find(qn("w:pgNumType"))
        if pgNum is None:
            pgNum = OxmlElement("w:pgNumType")
            sectPr.append(pgNum)
        pgNum.set(qn("w:start"), "1")


def montar_pre_textual(doc, resumo: str, palavras_chave: str,
                       abstract: str, key_words: str) -> None:
    """Insere capa, folha de rosto e bloco de pre-textual antes do corpo."""
    corpo = doc.element.body
    novos = []

    # --- CAPA -------------------------------------------------------------
    novos.append(_p(doc, UNIVERSIDADE, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER))
    novos.append(_p(doc, CURSO, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER))
    for _ in range(6):
        novos.append(_p(doc))
    novos.append(_p(doc, ALUNO, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER))
    for _ in range(6):
        novos.append(_p(doc))
    novos.append(_p(doc, TITULO_PT, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                    space_after=12))
    for _ in range(8):
        novos.append(_p(doc))
    novos.append(_p(doc, LOCAL_ANO[0], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER))
    novos.append(_p(doc, LOCAL_ANO[1], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER))

    # quebra de pagina -> folha de rosto
    ult = novos[-1].add_run()
    ult.add_break(WD_BREAK.PAGE)

    # --- FOLHA DE ROSTO ---------------------------------------------------
    novos.append(_p(doc, ALUNO, align=WD_ALIGN_PARAGRAPH.CENTER))
    for _ in range(8):
        novos.append(_p(doc))
    novos.append(_p(doc, TITULO_PT, bold=True,
                    align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12))
    novos.append(_p(doc))
    novos.append(_p(doc, "Trabalho de Conclusão de Curso apresentado como "
                         "requisito parcial para obtenção do grau de Bacharel "
                         "em Ciência da Computação.",
                    align=WD_ALIGN_PARAGRAPH.JUSTIFY))
    novos.append(_p(doc))
    novos.append(_p(doc, ORIENTADOR, align=WD_ALIGN_PARAGRAPH.RIGHT))
    for _ in range(5):
        novos.append(_p(doc))
    novos.append(_p(doc, LOCAL_ANO[0], align=WD_ALIGN_PARAGRAPH.CENTER))
    novos.append(_p(doc, LOCAL_ANO[1], align=WD_ALIGN_PARAGRAPH.CENTER))
    ult = novos[-1].add_run()
    ult.add_break(WD_BREAK.PAGE)

    # --- TÍTULO DO ARTIGO + AUTOR*/ORIENTADOR** ----------------------------
    # Elemento presente nos 10 TCC II aprovados e no .doc oficial do
    # Prof. Elvandi, ausente até 2026-10-05 (Bloco D da revisão completa).
    # Vai na página do Resumo, antes dele — mesmo padrão dos 10 aprovados
    # (confirmado em 3, estruturalmente idêntico nos demais).
    novos.append(_p(doc, TITULO_PT, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                    space_after=12))
    p_aluno = _p(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p_aluno.add_run(ALUNO_NOME_PROPRIO)
    r.font.name, r.font.size = "Arial", Pt(12)
    _ref_rodape(p_aluno, 1)
    novos.append(p_aluno)
    p_orient = _p(doc, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
    r = p_orient.add_run(ORIENTADOR_NOME_PROPRIO)
    r.font.name, r.font.size = "Arial", Pt(12)
    _ref_rodape(p_orient, 2)
    novos.append(p_orient)

    # --- RESUMO / ABSTRACT ------------------------------------------------
    p = _p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    r = p.add_run("Resumo: ")
    r.font.name, r.font.size, r.font.bold = "Arial", Pt(12), True
    r = p.add_run(resumo)
    r.font.name, r.font.size = "Arial", Pt(12)
    novos.append(p)

    p = _p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12)
    r = p.add_run("Palavras-chave: ")
    r.font.name, r.font.size, r.font.bold = "Arial", Pt(12), True
    r = p.add_run(palavras_chave)
    r.font.name, r.font.size = "Arial", Pt(12)
    novos.append(p)

    p = _p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    r = p.add_run("Abstract: ")
    r.font.name, r.font.size, r.font.bold = "Arial", Pt(12), True
    r = p.add_run(abstract)
    r.font.name, r.font.size = "Arial", Pt(12)
    novos.append(p)

    p = _p(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12)
    r = p.add_run("Key-words: ")
    r.font.name, r.font.size, r.font.bold = "Arial", Pt(12), True
    r = p.add_run(key_words)
    r.font.name, r.font.size = "Arial", Pt(12)
    novos.append(p)

    # SEM SUMÁRIO / LISTA DE ILUSTRAÇÕES / LISTA DE QUADROS — removido em
    # 2026-10-05 (Bloco B da revisão): os 10 TCC II aprovados usados como
    # referência (pasta "TCC II - EXEMPLOS E MATERIAIS") NÃO têm nenhum dos
    # três — em todos, a Introdução começa na página 3 ou 4, logo após
    # capa+folha de rosto+resumo/abstract, sem sumário nem listas no meio.
    # Confirmado nos 10, não só na maioria. O pré-textual deste artigo
    # termina no Abstract/Key-words; só falta a quebra de página pro corpo.
    ult = novos[-1].add_run()
    ult.add_break(WD_BREAK.PAGE)

    # tudo o que foi montado vai para o topo do corpo, nessa ordem
    for el in novos:
        corpo.remove(el._p)
    anchor = None
    for el in novos:
        if anchor is None:
            corpo.insert(0, el._p)
        else:
            anchor.addnext(el._p)
        anchor = el._p


def extrair_pre_textual(md: str) -> tuple[str, str, str, str]:
    """Puxa Resumo / Palavras-chave / Abstract / Key-words do markdown.

    re.M é obrigatório: sem ele `$` só casa no fim do arquivo, e nenhum
    destes blocos termina no fim.
    """
    def bloco(inicio: str, fim: str) -> str:
        m = re.search(inicio + r"(.*?)" + fim, md, re.S | re.M)
        if not m:
            return ""
        # Tira os marcadores de enfase: no pre-textual vai como texto simples,
        # igual ao TCC 1 ("Palavras-chave: esports; League of Legends; ...").
        return re.sub(r"\s+", " ", m.group(1).replace("*", "")).strip()

    resumo = bloco(r"^## RESUMO\s*$", r"^\*\*Palavras-chave:\*\*")
    palavras = bloco(r"^\*\*Palavras-chave:\*\*\s*", r"^\*\*Abstract:\*\*")
    abstract = bloco(r"^\*\*Abstract:\*\*\s*", r"^\*\*Key-words:\*\*")
    kwords = bloco(r"^\*\*Key-words:\*\*\s*", r"^---\s*$")
    return resumo, palavras, abstract, kwords


def _estilo(doc, *nomes):
    """Primeiro estilo existente entre os nomes dados (o reference-doc tem
    'FONTE DAS ILUSTRAÇÕES' e 'Fonte das ilustrações' — mesma coisa, caps
    diferentes)."""
    for n in nomes:
        try:
            return doc.styles[n]
        except KeyError:
            continue
    return None


def _campo_seq(paragrafo, identificador: str) -> None:
    """Insere {SEQ <id> \\* ARABIC} — numeração automática de Quadro/Figura.

   campo SEQ é o que permite a 'Lista de Quadros'/'Lista de Ilustrações'
    (TOC \\c) funcionar: sem ele o Word não tem como saber o que é_quadro.
    O Word recalcula o número ao abrir (Ctrl+A, F9) ou via finalize-fields.ps1.
    """
    run = paragrafo.add_run()
    for tipo, txt in (("begin", None), (None, f" SEQ {identificador} \\* ARABIC "),
                      ("separate", None), ("end", None)):
        if tipo:
            fld = OxmlElement("w:fldChar")
            fld.set(qn("w:fldCharType"), tipo)
            run._r.append(fld)
        else:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = txt
            run._r.append(instr)


def _legenda(doc, tipo: str, titulo: str) -> "docx.text.paragraph.Paragraph":
    """'Quadro 1 — Título'. Título ACIMA do elemento, por convenção ABNT."""
    p = doc.add_paragraph()
    try:
        p.style = doc.styles["Caption"]
    except KeyError:
        pass
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # achado da Bloco E (2026-10-05): sem isto, a paginação do Word pode
    # separar a legenda do quadro/figura que ela descreve (visto na Figura 1,
    # legenda sobrando sozinha no fim de uma página e a imagem na seguinte).
    p.paragraph_format.keep_with_next = True
    r = p.add_run(f"{tipo} ")
    r.font.name, r.font.size, r.font.bold = "Arial", Pt(10), True
    _campo_seq(p, tipo)
    r = p.add_run(f" — {titulo}")
    r.font.name, r.font.size, r.font.bold = "Arial", Pt(10), True
    return p


def _fonte(doc, texto: str) -> "docx.text.paragraph.Paragraph":
    """Linha de fonte OBRIGATÓRIA abaixo de quadro/figura (regra UNISINOS)."""
    p = doc.add_paragraph()
    st = _estilo(doc, "Fonte das ilustrações", "FONTE DAS ILUSTRAÇÕES")
    if st is not None:
        p.style = st
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run(texto)
    r.font.name, r.font.size, r.font.italic = "Arial", Pt(9), True
    return p


from docx.text.paragraph import Paragraph


def numerar_quadros(doc) -> int:
    """Insere legenda+fonte em cima e embaixo de cada tabela do corpo.

    O markdown marca os Quadros com uma linha 'Quadro - Título' antes da
    tabela; o pandoc vira essa linha em parágrafo normal. Aqui cada tabela
    ganha legenda com campo SEQ e a linha original é removida, para não
    duplicar o título.
    """
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    corpo = doc.element.body
    tabelas = [el for el in corpo.iterchildren() if el.tag.endswith("}tbl")]
    # a última tabela é a lista de arquivos do Anexo A, substituída por
    # figuras mais adiante — não recebe legenda de Quadro
    alvos = tabelas[:-1] if tabelas else []
    n = 0
    for tb, titulo in zip(alvos, QUADROS):
        # remove a linha "Quadro - ..." que vem imediatamente antes
        anterior = tb.getprevious()
        while anterior is not None and not anterior.tag.endswith("}p"):
            anterior = anterior.getprevious()
        if anterior is not None:
            txt = Paragraph(anterior, doc).text.strip()
            if txt.lower().startswith("quadro"):
                corpo.remove(anterior)
        leg = _legenda(doc, "Quadro", titulo)
        tb.addprevious(leg._p)
        larguras = LARGURAS_QUADROS.get(n)
        if larguras:
            ajustar_tabela(Table(tb, doc), larguras)
        fonte = _fonte(doc, FONTE_QUADROS)
        tb.addnext(fonte._p)
        n += 1
    return n


# página útil mede ~24,7cm de altura (A4 29,7cm - margens 3cm/2cm, ABNT) e
# as capturas do Anexo A são verticais (até 2812px de altura x 1440px de
# largura — telas de app, não paisagem): em largura fixa de 15cm elas davam
# 25-29cm de altura, MAIORES que a página inteira. Resultado (achado da
# Bloco E, 2026-10-05): a Figura 1 forçava quebra no meio da imagem e sua
# legenda ficava órfã na página anterior. 19cm de altura máxima deixa folga
# para legenda+fonte (~1-1,5cm) dentro dos 24,7cm úteis.
_FIGURA_LARGURA_MAX_CM = 15.0
_FIGURA_ALTURA_MAX_CM = 19.0


def _tamanho_figura(caminho: str):
    """Largura/altura (Cm) preservando proporção, sem estourar a página."""
    from PIL import Image
    from docx.shared import Cm

    with Image.open(caminho) as im:
        w_px, h_px = im.size
    largura = _FIGURA_LARGURA_MAX_CM
    altura = largura * h_px / w_px
    if altura > _FIGURA_ALTURA_MAX_CM:
        altura = _FIGURA_ALTURA_MAX_CM
        largura = altura * w_px / h_px
    return Cm(largura), Cm(altura)


def inserir_figuras(doc) -> int:
    """Troca a tabela-de-arquivos do Anexo A pelas 6 capturas com legenda.

    O markdown já avisava: 'não versionados neste Markdown - inserir como
    figura ao converter para o .docx final'.
    """
    from docx.table import Table
    from docx.shared import Cm

    pasta = os.path.join(ROOT, "reports", "anexo_a")
    faltando = [f for f, _ in FIGURAS if not os.path.exists(os.path.join(pasta, f))]
    if faltando:
        sys.exit(f"capturas ausentes em reports/anexo_a: {faltando}")

    corpo = doc.element.body
    tabelas = [el for el in corpo.iterchildren() if el.tag.endswith("}tbl")]
    if not tabelas:
        sys.exit("tabela do Anexo A não encontrada — o markdown mudou?")
    alvo = tabelas[-1]
    anterior = alvo.getprevious()
    while anterior is not None and not anterior.tag.endswith("}p"):
        anterior = anterior.getprevious()

    # a partir daqui os elementos são criados "no fim" e reinseridos antes da
    # tabela, que é removida no fim
    n = 0
    for arquivo, titulo in FIGURAS:
        leg = _legenda(doc, "Figura", titulo)
        alvo.addprevious(leg._p)
        largura, altura = _tamanho_figura(os.path.join(pasta, arquivo))
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.keep_with_next = True
        p_img.add_run().add_picture(
            os.path.join(pasta, arquivo), width=largura, height=altura
        )
        alvo.addprevious(p_img._p)
        fonte = _fonte(doc, FONTE_IMAGENS)
        alvo.addprevious(fonte._p)
        n += 1
    corpo.remove(alvo)
    if anterior is not None:
        # O parágrafo introdutório do Anexo A é conteúdo válido (documenta as
        # condições da captura) — só a ressalva "não versionados neste Markdown
        # - inserir como figura" fica obsoleta depois da conversão.
        p_intro = Paragraph(anterior, doc)
        txt = p_intro.text
        obsoleto = re.search(
            r"\(?não versionados?[^)]*\)?", txt, re.I
        )
        if obsoleto:
            novo = txt[: obsoleto.start()].rstrip()
            for r in list(p_intro.runs):
                r._r.getparent().remove(r._r)
            p_intro.add_run(novo + ".")
    return n


def formatar_referencias(doc) -> int:
    """Aplica o estilo REFERÊNCIAS e a separação de 1 linha em branco entre
    entradas.

    REGRA DO ORIENTADOR (Prof. Elvandi, em comentário no TCC 1, registrada
    em `docs/tcc2_texto.md` -> Pendências finais item 4): "Referências
    bibliográficas com 1 linha em branco separando cada entrada (norma
    ABNT)". O pandoc não faz isso — ele emite todas as entradas coladas em
    parágrafos `Normal`. Sem esta etapa o documento sai em desacordo com a
    correção que o próprio professor aplicou na versão anterior.

    O estilo REFERÊNCIAS também vem do TCC 1 (Arial 12, espaçamento após
    12pt) — é o estilo da instituição, não uma reconstrução local.
    """
    corpo = doc.element.body
    elementos = list(corpo.iterchildren())

    ini = None
    for i, el in enumerate(elementos):
        if not el.tag.endswith("}p"):
            continue
        p = Paragraph(el, doc)
        if p.text.strip().upper().startswith("REFERÊNCIAS") and \
           p.style.name.lower().startswith(("heading", "t")):
            ini = i
            break
    if ini is None:
        sys.exit("seção REFERÊNCIAS não encontrada")

    estilo_ref = _estilo(doc, "REFERÊNCIAS")
    n = 0
    entrada_anterior = None
    for el in elementos[ini + 1:]:
        if not el.tag.endswith("}p"):
            break
        p = Paragraph(el, doc)
        if p.style.name.lower().startswith(("heading", "t")):
            break  # acabou a seção (APÊNDICE A)
        if not p.text.strip():
            continue
        if estilo_ref is not None:
            p.style = estilo_ref
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        if entrada_anterior is not None:
            # linha em branco entre entradas
            br = entrada_anterior.add_run()
            br.add_break()
        entrada_anterior = p
        n += 1
    return n


def ajustar_tipografia(doc) -> None:
    """Aplica as medidas do MODELO OFICIAL do Prof. Elvandi (`TCC II - Modelo
    de artigo científico da UNISINOS - Exemplo Prof. Elvandi.doc`, convertido
    para .docx via automação do Word e lido direto do XML em 2026-10-05).

    MEDIDO NO XML DO ESTILO 'Normal' DO MODELO OFICIAL:
        fonte Arial 12 pt · margens 3,0/2,0/3,0/2,0 cm · entrelinha 1,5
        (`w:spacing w:line="360" w:lineRule="auto"`)
        recuo de parágrafo = 709 twips = 1,2506 cm ≈ **1,25 cm**
        (`w:ind w:firstLine="709"`) · justificado (`w:jc w:val="both"`)

    CORRIGE uma medição anterior (2026-10-04, pypdf sobre os 10 TCC II
    aprovados) que tinha concluído recuo ≈ 0 e descartado a regra de 1,25 cm
    do `Ajustes LATEX.txt`. Essa medição estava certa sobre o texto, mas o
    próprio plano que a gerou já avisava: "pypdf extrai texto, não layout; pra
    verificar recuo precisa-se gerar o .docx e conferir". O arquivo oficial do
    orientador, lido direto do XML (não por inferência de PDF), é a fonte que
    prevalece — é o documento que ele mesmo redigiu como modelo, e o usuário
    marcou seguir seu formato como obrigatório (2026-10-05).

    O ajuste vai no OBJETO DE ESTILO, não em `_p()`: `_p()` monta só o
    pré-textual e as legendas (~30 parágrafos). O corpo vem do pandoc com os
    estilos do `--reference-doc` (~1.500 parágrafos) — mexer só em `_p()`
    cobriria 2% do documento.
    """
    medido = {
        "recuo_cm": 1.25,       # 709 twips no XML do modelo oficial
        "entrelinha": 1.5,      # w:line="360" lineRule="auto" no modelo oficial
    }
    alvos = ("Normal", "Body Text", "First Paragraph", "Body Text Indent")
    aplicados = 0
    for nome in alvos:
        st = _estilo(doc, nome)
        if st is None:
            continue
        pf = st.paragraph_format
        pf.first_line_indent = Cm(medido["recuo_cm"])
        pf.line_spacing = medido["entrelinha"]
        aplicados += 1
    # a legenda de Quadro/Figura NÃO entra: recuo em legenda fica estranho
    # e a fonte das ilustrações é 9 pt (menor que o corpo), como nos aprovados.
    return aplicados


def aplicar_negrito_titulos(doc) -> int:
    """Força negrito + caixa alta nos estilos de título (Heading 1/2/3),
    seguindo o XML do estilo 'heading 1' do modelo oficial do Prof. Elvandi:

        <w:rPr><w:rFonts w:ascii="Arial Negrito".../><w:b/><w:caps/></w:rPr>

    Isto REVERTE a escolha anterior (2026-10-04, "sem negrito"), que vinha de
    um comentário manual do orientador numa revisão do TCC I — um sinal real,
    mas pontual e mais antigo. O modelo oficial de artigo (este arquivo) é a
    fonte que o usuário marcou como obrigatória em 2026-10-05, e define
    negrito+caixa alta como regra do estilo, não como exceção pontual. Entre
    os dois sinais do mesmo orientador, prevalece o mais explícito e atual.

    `w:caps` é só exibição (maiúsculas visuais) — não precisa alterar o texto
    literal, que já é digitado em caixa alta nos títulos do markdown-fonte.

    ACHADO DO BLOCO E (leitura humana ponta a ponta, 2026-10-05): o estilo
    'Heading 1' herdado do TCC I tem `space_before=None` (sem espaço ANTES
    do título) enquanto 'Heading 2'/'Heading 3' já tinham 18pt — visível na
    revisão visual como "4 METODOLOGIA" colado no parágrafo anterior,
    diferente de toda subseção. O modelo oficial do professor define
    before=after=360 twips (18pt) nos TRÊS níveis; já tínhamos o "depois"
    certo nos três e o "antes" certo só em H2/H3 — gap que nenhuma
    checagem anterior cobria (conferi "depois" nos três, não o "antes"
    de H1 especificamente). Corrigido aqui, não só em H2/H3.
    """
    aplicados = 0
    for nome in ("Heading 1", "Heading 2", "Heading 3"):
        st = _estilo(doc, nome)
        if st is None:
            continue
        st.font.bold = True
        st.font.all_caps = True
        st.paragraph_format.space_before = Pt(18)
        aplicados += 1
    return aplicados


def ajustar_tabela(tabela, larguras_cm: list[float]) -> None:
    """Fixa larguras de coluna e reduz o corpo da tabela.

    Sem isto o Word distribui as colunas por conteúdo e a coluna `#` de um
    número de 1 dígito fica com um terço da largura da tabela — foi o que
    denunciou o Quadro 3 (benchmark NLQ), em que a coluna de SQL devolvia a
    largura que as outras não precisavam e as linhas ficavam altíssimas.
    """
    # A contagem de larguras tem que bater com a contagem de colunas. Sem
    # esta guarda o `zip` abaixo trunca em silencio: o Quadro 1 estava com
    # 5 larguras declaradas para 3 colunas e saia com 7,2 cm dos 16 cm
    # uteis, sem nenhuma falha em lugar nenhum.
    n_colunas = len(tabela.columns)
    if len(larguras_cm) != n_colunas:
        raise SystemExit(
            f"largura de tabela divergente: {len(larguras_cm)} declaradas para "
            f"{n_colunas} colunas. O `zip` trunca em silencio e a tabela sai "
            f"estreita sem erro. Corrija LARGURAS_QUADROS."
        )
    tabela.autofit = False
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    for linha in tabela.rows:
        for celula, larg in zip(linha.cells, larguras_cm):
            celula.width = Cm(larg)
            for p in celula.paragraphs:
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.0
                for r in p.runs:
                    r.font.name = "Arial"
                    # 9 pt no corpo da tabela: 12 pt deixava o Quadro 3 com
                    # 27 páginas de tabela, o que estourava o limite de 25-30
                    r.font.size = Pt(9)
    # repetem a largura no grid, que é o que o Word usa para renderizar
    grid = tabela._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for col, larg in zip(grid.findall(qn("w:gridCol")), larguras_cm):
            col.set(qn("w:w"), str(int(larg * 567)))  # cm -> twips


# Larguras por quadro, em cm (soma ~16 cm = área útil entre margens 3+2).
# O que o texto usa como legenda define a ordem das colunas.
# A contagem de entradas tem que ser a de colunas do quadro: `ajustar_tabela`
# levanta se divergir, porque o `zip` trunca em silencio e a falha não aparece
# em nenhuma checagem. Foi assim que o Quadro 1 saiu com 5 larguras e 3 colunas.
LARGURAS_QUADROS = {
    0: [2.8, 4.2, 9.0],                         # vitória do vermelho por região
    1: [3.4, 2.5, 2.3, 2.1, 2.3, 3.4],         # comparação entre modelos
    2: [3.0, 9.5, 3.5],                         # esquema relacional do banco
    3: [0.8, 4.4, 7.4, 3.4],                    # benchmark NLQ (o problema)
    4: [1.6, 1.6, 2.0, 2.4, 1.8, 1.8, 1.4, 1.4, 1.8],   # métricas por corte
    5: [0.9, 6.1, 9.0],                         # experimentos negativos
}


def main() -> None:
    ref = os.environ.get("TCC1_REFERENCE_DOCX", "")
    if not ref or not os.path.exists(ref):
        sys.exit(
            "Defina TCC1_REFERENCE_DOCX apontando para o TCC 1 (.docx).\n"
            "Ele e usado como documento de referencia de ESTILO (fontes, "
            "margens, espacamento) - o conteudo nao e lido.\n"
            "Exemplo:\n"
            "  $env:TCC1_REFERENCE_DOCX='C:\\Users\\Home\\Downloads\\TCC\\TCC_Final.docx'\n"
            "  .venv\\Scripts\\python.exe docs\\build_tcc_docx.py"
        )

    md_bruto = preprocessar()
    resumo, palavras, abstract, kwords = extrair_pre_textual(
        open(MD, encoding="utf-8").read()
    )
    for nome, val in (("resumo", resumo), ("palavras-chave", palavras),
                      ("abstract", abstract), ("key-words", kwords)):
        if not val:
            sys.exit(f"falha ao extrair '{nome}' do markdown - revise a regex")

    with open(STAGE, "w", encoding="utf-8") as f:
        f.write(md_bruto)

    print(f"[1/3] markdown limpo: {len(md_bruto.split())} palavras")
    rodar_pandoc(STAGE, ref)
    print("[2/3] pandoc gerou o corpo do .docx")

    doc = docx.Document(STAGE)
    n_tipografia = ajustar_tipografia(doc)
    n_titulos = aplicar_negrito_titulos(doc)
    montar_pre_textual(doc, resumo, palavras, abstract, kwords)
    _adicionar_rodapes(doc, {1: NOTA_ALUNO, 2: NOTA_ORIENTADOR})
    n_q = numerar_quadros(doc)
    n_f = inserir_figuras(doc)
    n_r = formatar_referencias(doc)
    _numeracao_comeca_em_um(doc)
    doc.save(OUT)
    os.remove(STAGE)
    print(f"[3/4] pre-textual montado (sem sumario/listas, ver nota em "
          f"montar_pre_textual) | tipografia ajustada em {n_tipografia} "
          f"estilo(s) (recuo 1,25cm e entrelinha 1,5, medidos no .doc oficial "
          f"do Prof. Elvandi) | {n_titulos} estilo(s) de titulo em negrito+caixa "
          f"alta (idem)")
    print(f"[4/4] {n_q} Quadros numerados (campo SEQ) + {n_f} Figuras "
          f"inseridas + {n_r} referências no estilo REFERÊNCIAS com 1 "
          f"linha em branco entre entradas")
    print(f"       -> {OUT}")
    print(f"       paragrafos: {len(doc.paragraphs)} | tabelas: {len(doc.tables)}")
    print("       falta: docs/finalize-fields.ps1 (Word atualiza a "
          "numeracao dos campos SEQ)")


if __name__ == "__main__":
    main()