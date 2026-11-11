"""Gera `docs/roteiro_citacoes.md`: cada frase do TCC que cita uma obra, com
página, seção e a obra citada, para a validação de plágio (plano em
`docs/plano_validacao_plagio.md`, itens 1 e 2).

POR QUE EXISTE: quase todas as 31 referências são em inglês e o texto é em
português. Detectores de similaridade comparam no mesmo idioma e não pegam
paráfrase próxima de uma tradução; a Cartilha de plágio da Unisinos trata
"colcha de retalhos" e "citação de obra que não foi pesquisada" como plágio.
O que pega isso é ler cada frase ao lado da fonte. Este script só monta a
lista; não julga nada.

Lê o `.docx` entregue (não o markdown) e, se existir, um PDF exportado pelo
Word para descobrir a página de cada frase.

Uso:
    .venv\\Scripts\\python.exe docs\\gera_roteiro_citacoes.py [caminho.pdf]
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from docx import Document

RAIZ = Path(__file__).resolve().parent.parent
DOCX = RAIZ / "docs" / "tcc2_final.docx"
SAIDA = RAIZ / "docs" / "roteiro_citacoes.md"
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Sobrenomes que abrem as 31 entradas da lista de referências (lidos do
# próprio .docx abaixo); a chamada no texto usa a grafia "Breiman" ou "BREIMAN".
ANO = r"(?:19|20)\d{2}|\[s\.d\.\]"


def entradas_referencias(paragrafos: list[str]) -> list[tuple[str, str]]:
    i = next(k for k, p in enumerate(paragrafos) if p.strip() == "REFERÊNCIAS")
    fim = next(k for k in range(i + 1, len(paragrafos)) if paragrafos[k].startswith("APÊNDICE"))
    refs = []
    for p in paragrafos[i + 1:fim]:
        p = p.strip()
        if not p:
            continue
        sobrenome = re.split(r"[,.]", p)[0].strip()
        # o ano de publicação vem antes de DOI, "Disponível em" e "Acesso em";
        # pegar o último ano da entrada inteira devolvia a data de acesso (2026)
        # ou um número de DOI (TG.2019)
        nucleo = re.split(r"\b(?:DOI|Disponível em|Acesso em)\b", p)[0]
        ano = re.findall(r"\b(?:19|20)\d{2}\b", nucleo)
        refs.append((sobrenome, ano[-1] if ano else "[s.d.]"))
    return refs


def frases(texto: str) -> list[str]:
    # corta em ponto final seguido de espaço e maiúscula, sem cortar "et al." nem "[s.d.]"
    # o lookbehind tem de incluir o ponto: o corte acontece DEPOIS dele, e a
    # versão "(?<!et al)" deixava "Hodge et al." como frase separada, sem o ano
    partes = re.split(r"(?<!et al\.)(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ“\"(])", texto)
    return [p.strip() for p in partes if p.strip()]


def main() -> None:
    d = Document(str(DOCX))
    paragrafos = [p.text for p in d.paragraphs]
    refs = entradas_referencias(paragrafos)
    padroes = []
    for sobrenome, ano in refs:
        # capitaliza cada parte separada por espaço ou hífen: str.title() fazia
        # "Oracle’S Elixir", e cortar só no espaço fazia "García-méndez"
        nome = ("".join(t[:1] + t[1:].lower() for t in re.split(r"([ -])", sobrenome))
                if sobrenome.isupper() else sobrenome)
        # "Breiman (2001)", "Breiman e ...", "(Breiman, 2001)", "BREIMAN, 2001", "Hodge et al. (2021)"
        alt = re.escape(nome).replace(r"\ ", r"\s+")
        padroes.append((f"{sobrenome} ({ano})",
                        # janela livre: a antiga, [^.], parava no ponto de "et al." e perdia Hodge, Guo...
                        # sem re.I; sobrenome curto ("Do", "Gil") só conta com o ano colado
                        # ("Do et al. (2021)", "(Gil, 2002)"): "Do" casava com a preposição
                        # "do" e inflava a contagem
                        # o ano exigido é o da própria obra: com qualquer ano, "Wallner, Wang
                        # e Dormann (2023)" contava como Wang (2020)
                        re.compile(rf"\b(?:{alt}|{re.escape(sobrenome)})\b"
                                   + (rf"(?:\s+et\s+al\.)?\s*[,(]\s*{re.escape(ano)}" if len(nome) <= 3
                                      else rf"(?=[^()]{{0,80}}?\(?[^()]{{0,40}}?{re.escape(ano)})"))))

    pdf_paginas: list[str] = []
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        import pymupdf
        doc_pdf = pymupdf.open(sys.argv[1])
        pdf_paginas = [re.sub(r"\s+", " ", p.get_text()) for p in doc_pdf]

    def pagina(frase: str) -> str:
        if not pdf_paginas:
            return "—"
        alvo = re.sub(r"\s+", " ", frase)[:60]
        for n, t in enumerate(pdf_paginas, 1):
            if alvo in t:
                return str(n)
        return "?"

    inicio = next(k for k, p in enumerate(paragrafos) if p.startswith("Resumo:"))
    fim = next(k for k, p in enumerate(paragrafos) if p.strip() == "REFERÊNCIAS")
    secao = "Resumo"
    linhas = []
    por_obra: dict[str, int] = defaultdict(int)
    for p in paragrafos[inicio:fim]:
        if re.match(r"^\d+(\.\d+)*\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", p) and len(p) < 120:
            secao = p.strip()[:60]
            continue
        for f in frases(p):
            obras = [rotulo for rotulo, rx in padroes if rx.search(f)]
            if not obras:
                continue
            for o in obras:
                por_obra[o] += 1
            linhas.append((pagina(f), secao, "; ".join(obras), f))

    # citações em quadros (Quadro 25 resume os métodos com a obra de cada um)
    quadro_cit = []
    for t in d.tables:
        for r in t.rows:
            celula = " | ".join(c.text for c in r.cells)
            obras = [rotulo for rotulo, rx in padroes if rx.search(celula)]
            if obras:
                quadro_cit.append(("; ".join(obras), celula))
                for o in obras:
                    por_obra[o] += 1

    nao_citadas = [f"{s} ({a})" for s, a in refs if por_obra.get(f"{s} ({a})", 0) == 0]
    out = ["# Roteiro de citações do TCC II (gerado)", "",
           f"Gerado por `docs/gera_roteiro_citacoes.py` a partir de `docs/tcc2_final.docx`. "
           "Serve para os itens 1 e 2 do `docs/plano_validacao_plagio.md`: ler cada frase "
           "ao lado do trecho da fonte e anotar (a) a página ou seção da fonte que a sustenta e "
           "(b) se a redação está próxima demais do original (paráfrase de tradução).", "",
           f"**{len(linhas)} frases no texto e {len(quadro_cit)} linhas de quadro citam "
           f"{len([o for o in por_obra if por_obra[o]])} das {len(refs)} obras da lista de referências.**", ""]
    if nao_citadas:
        out += ["Obras da lista sem chamada detectada (conferir à mão; pode ser grafia diferente):", ""]
        out += [f"- {o}" for o in nao_citadas] + [""]
    out += ["## Frases do texto", "",
            "| # | Pág. | Seção | Obra(s) | Frase | Trecho da fonte que sustenta | Redação própria? |",
            "|---|---|---|---|---|---|---|"]
    for i, (pg, sec, obras, f) in enumerate(linhas, 1):
        out.append(f"| {i} | {pg} | {sec} | {obras} | {f.replace('|', '/')} |  |  |")
    out += ["", "## Linhas de quadro", "", "| Obra(s) | Linha |", "|---|---|"]
    for obras, cel in quadro_cit:
        out.append(f"| {obras} | {cel.replace('|', '/')[:300]} |")
    out += ["", "## Chamadas por obra", "", "| Obra | Ocorrências |", "|---|---:|"]
    for s, a in refs:
        out.append(f"| {s} ({a}) | {por_obra.get(f'{s} ({a})', 0)} |")
    SAIDA.write_text("\n".join(out) + "\n", encoding="utf-8")
    sem_pagina = sum(1 for l in linhas if l[0] == "?")
    print(f"{len(linhas)} frases, {len(quadro_cit)} linhas de quadro, {len(refs)} referências; "
          f"sem chamada detectada: {len(nao_citadas)}; frases sem página achada: {sem_pagina}")
    print(f"-> {SAIDA}")


if __name__ == "__main__":
    main()
