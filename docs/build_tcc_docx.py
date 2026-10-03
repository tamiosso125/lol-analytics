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
     os estilos;
  3. python-docx monta capa e folha de rosto (que o pandoc nao faz), insere
     o campo SUMARIO e comeca a numeracao de paginas no corpo.

Uso:  .venv\\Scripts\\python.exe docs\\build_tcc_docx.py
Depende de pandoc no PATH (winget install JohnMacFarlane.Pandoc).
"""
import os
import re
import subprocess
import sys

import docx
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "docs", "tcc2_texto.md")
OUT = os.path.join(ROOT, "docs", "tcc2_final.docx")
STAGE = os.path.join(ROOT, "docs", ".build_tcc_stage.md")

# Identidade e metadados extraidos do TCC 1 (TCC_Final.docx, aprovado) e do
# modelo oficial da UNISINOS de 2026-09-28. NAO sao inventados: o nome, o curso,
# a cidade, o ano, o orientador e o formato de capa/folha foram lidos dos
# arquivos citados.
ALUNO = "GUILHERME RIBEIRO LEMOS TAMIOSSO"
CURSO = "GRADUAÇÃO EM CIÊNCIA DA COMPUTAÇÃO"
UNIVERSIDADE = "UNIVERSIDADE DO VALE DO RIO DOS SINOS (UNISINOS)"
ORIENTADOR = "Orientador: Prof. Dr. Elvandi da Silva Júnior"
LOCAL_ANO = ("Porto Alegre", "2026")
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
    "(Chromium, 1440×900) contra a API e o frontend locais."
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

    # --- SUMÁRIO ----------------------------------------------------------
    ult = novos[-1].add_run()
    ult.add_break(WD_BREAK.PAGE)
    novos.append(_p(doc, "SUMÁRIO", bold=True,
                    align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18))
    p = _p(doc)
    _campo(p, r'TOC \o "1-3" \h \z \u')
    novos.append(p)
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
        fonte = _fonte(doc, FONTE_QUADROS)
        tb.addnext(fonte._p)
        n += 1
    return n


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
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(os.path.join(pasta, arquivo), width=Cm(15))
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


def listas_de_ilustracoes(doc, resumos: dict) -> None:
    """Lista de Ilustrações + Lista de Quadros no pre-textual.

    São campos TOC \\c — dependem dos campos SEQ das legendas. O Word
    preenche quando os campos são atualizados (finalize-fields.ps1).
    """
    corpo = doc.element.body
    # insere logo após o campo do SUMÁRIO, que é o penúltimo parágrafo do
    # pre-textual montado no passo 3
    paras = [el for el in corpo.iterchildren() if el.tag.endswith("}p")]
    ancora = None
    for el in reversed(paras):
        tem_sumario = el.findall(".//" + qn("w:instrText"))
        if any("TOC" in (i.text or "") for i in tem_sumario):
            ancora = el
            break
    if ancora is None:
        sys.exit("campo do SUMÁRIO não encontrado — listas não inseridas")

    def bloco(titulo: str, ident: str, instrucao: str, depois_de):
        """Monta título + campo TOC e reinsere logo após `depois_de`.

        A âncora é passada explicitamente porque `addnext` inserir sempre
        na mesma âncora inverte a ordem das listas.
        """
        t = _p(doc, titulo, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT,
               space_after=12)
        corpo.remove(t._p)
        depois_de.addnext(t._p)
        p = doc.add_paragraph()
        _campo(p, instrucao)
        corpo.remove(p._p)
        t._p.addnext(p._p)
        p.paragraph_format.line_spacing = 1.0
        p.add_run().add_break(WD_BREAK.PAGE)
        return p._p

    # ordem do modelo: Lista de Ilustrações antes da Lista de Quadros
    l1 = bloco("LISTA DE ILUSTRAÇÕES", "Figura",
               r'TOC \h \z \c "Figura"', ancora)
    bloco("LISTA DE QUADROS", "Quadro", r'TOC \h \z \c "Quadro"', l1)
    resumos["listas"] = 2


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
    montar_pre_textual(doc, resumo, palavras, abstract, kwords)
    n_q = numerar_quadros(doc)
    n_f = inserir_figuras(doc)
    n_r = formatar_referencias(doc)
    listas_de_ilustracoes(doc, {})
    _numeracao_comeca_em_um(doc)
    doc.save(OUT)
    os.remove(STAGE)
    print(f"[3/4] pre-textual montado")
    print(f"[4/4] {n_q} Quadros numerados (campo SEQ) + {n_f} Figuras "
          f"inseridas + {n_r} referências no estilo REFERÊNCIAS com 1 "
          f"linha em branco entre entradas")
    print(f"       -> {OUT}")
    print(f"       paragrafos: {len(doc.paragraphs)} | tabelas: {len(doc.tables)}")
    print("       falta: docs/finalize-fields.ps1 (Word atualiza SUMARIO, "
          "LISTA DE QUADROS e a numeracao dos campos SEQ)")


if __name__ == "__main__":
    main()