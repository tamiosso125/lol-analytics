"""Verificacao de consistencia do texto do TCC II.

Roda as checagens que o AGENTS.md exige antes de dar um trabalho por pronto, e
que antes eram feitas a mao (e por isso falhavam):

  1. nenhum caractere CJK/cirilico escapado no texto PT-BR;
  2. toda referencia cruzada "Seção N.M" aponta para uma seção que existe;
  3. os numeros citados na conclusão batem com o quadro de métricas;
  4. nenhuma tabela do texto tem coluna com contagem incompatível com o
     cabeçalho;
  5. as referências ABNT estão em ordem alfabética e sem entradas duplicadas;
  6. os números de desempenho citados no texto existem no relatório de
     métricas por corte (guards de regressão numérica).

Uso:
    .venv\\Scripts\\python.exe docs\\verifica_tcc.py
Exit code 0 = tudo consistente.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TEXTO = RAIZ / "docs" / "tcc2_texto.md"
FALHAS: list[str] = []
AVISOS: list[str] = []

# O console do Windows e cp1252 e morre em seta, aspas tipograficas e
# qualquer caractere nao-latino — inclusive o texto que a checagem precisa
# mostrar. Sem isto o script levanta UnicodeEncodeError no meio da lista de
# falhas e nao diz qual era a falha, que e o oposto do objetivo dele.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass


def falha(msg: str) -> None:
    FALHAS.append(msg)


def aviso(msg: str) -> None:
    AVISOS.append(msg)


def check_cjk(t: str) -> None:
    maus = re.findall(r"[\u3000-\u9fff\u0400-\u04ff\uac00-\ud7af]", t)
    if maus:
        for c in sorted(set(maus)):
            i = t.find(c)
            linha = t[:i].count("\n") + 1
            falha(f"caractere nao latino U+{ord(c):04X} na linha {linha}: {c!r}")
    else:
        print("  [OK] nenhum caractere CJK/cirilico no texto")


def check_referencias_cruzadas(t: str) -> None:
    secs = set()
    for m in re.finditer(r"(?m)^#{1,4}\s+(\d+(?:\.\d+)*)\s+", t):
        secs.add(m.group(1))
    quebradas = []
    for m in re.finditer(r"Se[çc][ãa]o\s+(\d+(?:\.\d+)*)", t):
        if m.group(1) not in secs:
            quebradas.append((t[: m.start()].count("\n") + 1, m.group(1)))
    for ln, s in quebradas:
        falha(f"linha {ln}: referência cruzada 'Seção {s}' sem seção correspondente")
    if not quebradas:
        print(f"  [OK] todas as referencias cruzadas resolvem ({len(secs)} secoes)")


def check_abelas(t: str) -> None:
    """Cada tabela markdown precisa ter o mesmo numero de celulas em todas as linhas."""
    blocos = re.findall(r"(?m)(?:^\|.*\|$\n)+", t)
    for bi, bloco in enumerate(blocos, 1):
        linhas = [l for l in bloco.strip().split("\n") if l.strip()]
        if len(linhas) < 2:
            continue
        larguras = {len(re.findall(r"(?<!\\)\|", l)) for l in linhas}
        if len(larguras) > 1:
            falha(f"tabela {bi}: larguras de coluna inconsistentes {sorted(larguras)}")
    print(f"  [OK] {len(blocos)} tabelas markdown com colunas consistentes")


def check_ordem_referencias(t: str) -> None:
    i, j = t.find("## REFER"), t.find("## AP")
    if i < 0:
        aviso("secao REFERENCIAS nao encontrada")
        return
    bloco = t[i:j]
    # Uma entrada por BLOCO separado por linha em branco. Sem isso, uma linha
    # de continuacao como "COMPUTER VISION, IMAGING AND COMPUTER GRAPHICS"
    # (continuacao de BAHROLOLLOOMI) entra na lista como se fosse entrada
    # propria e acusa ordem errada — foi o que aconteceu na primeira versao.
    entradas = [b.strip() for b in re.split(r"\n\s*\n", bloco) if b.strip()]
    # o bloco inclui o cabecalho "## REFERENCIAS" e o "---" final: nao sao
    # entradas bibliograficas e precisam sair antes da contagem
    entradas = [e for e in entradas
                if not e.startswith("#") and e.strip() != "---"]
    chaves = []
    for entrada in entradas:
        primeira = entrada.split("\n", 1)[0].strip()
        # sobrenome: "SOBRENOME,resto", "SOBRENOME; resto" ou
        # "NOME INSTITUICAO. **Titulo**" (ex.: RIOT GAMES. APIs.).
        # O HIFEN precisa estar na classe: sem ele "GARCÍA-MÉNDEZ" nao casa
        # e a entrada fica de fora da checagem de ordem — exatamente o tipo de
        # cobertura silenciosa que faz a checagem parecer mais forte que e.
        m = re.match(r"([A-ZÀ-Ú][A-ZÀ-Ú' \-]*?)(?:[;,.]|\s-\s)", primeira)
        if m:
            chaves.append(m.group(1).strip().lower())
    for a, b in zip(chaves, chaves[1:]):
        if a > b:
            falha(f"referencias fora de ordem alfabetica: {a!r} antes de {b!r}")
    dups = {c for c in chaves if chaves.count(c) > 1}
    for d in sorted(dups):
        falha(f"referencia duplicada: {d!r}")
    # a contagem tem que bater com o número de entradas: se a regex perder
    # alguma, o "[OK] N referencias" mente sobre a cobertura da checagem.
    if len(chaves) != len(entradas):
        aviso(f"a extração de sobrenomes pegou {len(chaves)} de "
              f"{len(entradas)} entradas: revise a regex")
    if not any("alfabetica" in f or "duplicada" in f for f in FALHAS):
        print(f"  [OK] {len(chaves)} referencias em ordem alfabetica e sem duplicatas")


def check_numeros_modelo(t: str) -> None:
    """O XGBoost de produção cited no texto tem que bater com o relatório."""
    rel = RAIZ / "reports" / "metricas_corte.json"
    if not rel.exists():
        aviso("reports/metricas_corte.json ausente: guarda de numero nao roda "
              "(gere com python -m src.models.multi_cutoff_metrics)")
        return
    try:
        bruto = json.loads(rel.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        falha(f"reports/metricas_corte.json invalido: {exc}")
        return
    # o script grava {"gerado_em":..., "resultados": {"15": {"XGBoost": {...}}}}
    # (as chaves de corte sao "10","15","20","25" — sem o sufixo "min")
    dados = bruto.get("resultados", bruto)
    xg15 = dados.get("15", {}).get("XGBoost")
    if not isinstance(xg15, dict):
        aviso("formato de reports/metricas_corte.json nao reconhecido")
        return
    acc = xg15.get("acuracia")
    auc = xg15.get("auc")
    if acc is None:
        aviso("campo de acuracia ausente no relatorio")
        return
    # o texto escreve com virgula decimal
    acc_txt = f"{acc:.4f}".replace(".", ",")
    auc_txt = f"{auc:.4f}".replace(".", ",") if auc else None
    achou_acc = acc_txt in t
    if not achou_acc:
        falha(f"aceracia do XGBoost ({acc_txt}) nao aparece no texto — "
              "numero do texto e do relatorio divergem")
    else:
        print(f"  [OK] acuracia do XGBoost ({acc_txt}) confere com o relatorio")
    if auc_txt and auc_txt not in t:
        falha(f"AUC do XGBoost ({auc_txt}) nao aparece no texto")
    elif auc_txt:
        print(f"  [OK] AUC do XGBoost ({auc_txt}) confere com o relatorio")


def check_quadro_regioes(t: str) -> None:
    """O Quadro 1 (vitória do vermelho por região) tem que bater com o banco.

    Já aconteceu: a tabela ficou com NA1 = 1.446 / 51,9% enquanto o banco
    já tinha 7.159 / 52,2%. Duas rodadas de coleta depois, a tabela ainda
    descrevia a base antiga — e era o único lugar do documento onde a
    fragilidade da NA1 continuava visível ao leitor. Se o banco não estiver
    acessível, isso vira aviso e não falha: a checagem é adicional.
    """
    import re as _re

    linhas = _re.findall(r"(?m)^\| (BR1|EUW1|KR|NA1|EUN1) \| ([\d.]+) \| ([\d,]+)%", t)
    if not linhas:
        aviso("Quadro 1 por regiao nao encontrado no texto")
        return
    try:
        import sys

        sys.path.insert(0, str(RAIZ))
        from src.db import get_conn  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        aviso(f"banco inacessivel, comparacao regional pulada: {exc}")
        return
    try:
        cur = get_conn().cursor()
        # team_id 200 = vermelho. Filtrar por ele e testar v_red > 0 e o que
        # faz a taxa cair a 50,0% em toda regiao quando se mede sobre
        # `participants` direto: `win` e por jogador, e a media de uma coluna
        # que soma cinco por partida e sempre 50% por simetria.
        cur.execute(
            """
            SELECT split_part(match_id,'_',1),
                   COUNT(*),
                   ROUND(100.0*AVG(CASE WHEN v_red > 0 THEN 1 ELSE 0 END)::numeric, 1)
            FROM (SELECT match_id, SUM(CASE WHEN win THEN 1 ELSE 0 END) AS v_red
                  FROM participants WHERE team_id = 200 GROUP BY match_id) t
            GROUP BY 1
            """
        )
        real = {r[0]: (r[1], f"{r[2]:.1f}") for r in cur.fetchall()}
    except Exception as exc:  # noqa: BLE001
        aviso(f"consulta regional falhou: {exc}")
        return

    for regiao, n_txt, pct_txt in linhas:
        if regiao not in real:
            aviso(f"Quadro 1 cita {regiao}, que nao existe no banco")
            continue
        n_real, pct_real = real[regiao]
        n_txt = n_txt.replace(".", "")
        # o texto escreve "56,3%" e o banco devolve 56.3 — normalizar os dois
        # para float, senao a comparacao quebra em ValueError e a checagem
        # morre em vez de dizer o que divergiu.
        if abs(float(pct_txt.replace(",", ".")) - float(pct_real)) > 0.05:
            falha(f"Quadro 1: {regiao} com {pct_txt}% no texto, "
                  f"{pct_real}% no banco")
        if int(n_txt) != int(n_real):
            falha(f"Quadro 1: {regiao} com {int(n_txt)} partidas no texto, "
                  f"{n_real} no banco")
    if not any("Quadro 1" in f for f in FALHAS):
        print(f"  [OK] Quadro 1 confere com o banco ({len(linhas)} regioes)")


def check_profissional(t: str) -> None:
    """Contagem de jogos profissionais e taxa do azul x banco.

    O texto afirmava 99.259 jogos profissionais; o banco tem 96.716. O erro
    sobreviveu a dois ciclos de coleta porque ninguem contava. A contagem
    correta e `COUNT(DISTINCT game_id)`: `pro_games` guarda DUAS linhas por
    jogo (uma por time, nao uma por jogador), entao `COUNT(*)` devolve o
    dobro — 193.432 — e parece um numero plausivel.
    """
    m = _re_num(r"(\d{2}\.\d{3})\s+(?:jogos|partidas)\s+profissionais", t)
    if not m:
        aviso("contagem de jogos profissionais nao encontrada no texto")
        return
    txt = int(m.group(1).replace(".", ""))
    try:
        import sys

        sys.path.insert(0, str(RAIZ))
        from src.db import get_conn  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        aviso(f"banco inacessivel, contagem profissional pulada: {exc}")
        return
    try:
        cur = get_conn().cursor()
        cur.execute("SELECT COUNT(DISTINCT game_id) FROM pro_games")
        real = cur.fetchone()[0]
        cur.execute("""SELECT ROUND(100.0*AVG(CASE WHEN win THEN 1 ELSE 0 END)::numeric,1)
                       FROM pro_games WHERE side='Blue'""")
        pct_azul = cur.fetchone()[0]
    except Exception as exc:  # noqa: BLE001
        aviso(f"consulta profissional falhou: {exc}")
        return
    if txt != real:
        falha(f"jogos profissionais: {txt} no texto, {real} no banco")
        return
    pct_txt = f"{pct_azul:.1f}".replace(".", ",")
    if f"{pct_txt}%" not in t:
        aviso(f"taxa do azul no profissional ({pct_txt}%) nao aparece no texto")
    print(f"  [OK] jogos profissionais {real} e taxa do azul {pct_txt}% "
          f"conferem com o banco")


def _re_num(padrao: str, t: str):
    import re as _re

    return _re.search(padrao, t)


# Valores que NUNCA devem aparecer em lugar nenhum do texto: foram
# substituidos por retreino, por remocao do dataset, ou por achado refutado.
#
# A checagem de presenca acima (acuracia no texto) passa mesmo com o valor
# velho ainda la — ela so pergunta se o numero novo existe, nao se o antigo
# sumiu. Foi exatamente essa lacuna que deixou 0,7573 no texto e fez o
# Abstract em ingles repetir a forma refutada do achado por meses.
VALORES_SUBSTITUIDOS: list[tuple[str, str]] = [
    ("0,7573", "acuracia do XGBoost antes do retreino de 39.188"),
    ("0,8219", "AUC do Random Forest antes do retreino"),
    ("46,3%", "taxa do azul aos 15 min, do periodo em que se acreditava no pico"),
    ("84,0%", "conversao de vantagem no profissional, antes da remedicao"),
    ("33.713", "tamanho da base entre 2026-10-03 e 2026-10-04"),
    ("99.259", "contagem de jogos profissionais, nunca conferida"),
]
# NAO entra em VALORES_SUBSTITUIDOS: 0,8319 e 0,8295 sao o experimento 9 do
# Apendice D, medido legitimamente sobre a base de 23.133. O que o texto
# precisa e da anotacao de base ao lado, para o leitor poder julgar — nao da
# proibicao do numero.

# A forma REFUTADA do achado de lado, nos dois idiomas. Enquanto o texto
# afirmar que o vies enfraquece ao longo da partida, ele contradiz a Secao 5.3
# e a bateria de testes.
PADROES_REFUTADOS: list[tuple[str, str]] = [
    (r"enfraquece\s+ao\s+longo\s+da\s+partida", "forma refutada do vies"),
    (r"n[ãa]o\s+[ée]\s+constante\s+ao\s+longo", "forma refutada do vies"),
    (r"weakens\s+over\s+the\s+course", "forma refutada do vies (abstract)"),
    (r"weakens\s+over", "forma refutada do vies (abstract)"),
]


def check_residuos(t: str) -> None:
    """Nenhum valor substituido e nenhuma forma refutada pode sobrar no texto."""
    import re as _re

    for valor, porque in VALORES_SUBSTITUIDOS:
        for m in _re.finditer(_re.escape(valor), t):
            linha = t[: m.start()].count("\n") + 1
            trecho = t.splitlines()[linha - 1].strip()[:78]
            falha(f"linha {linha}: valor substituido {valor} ainda presente "
                  f"({porque}) -> {trecho!r}")
    for padrao, porque in PADROES_REFUTADOS:
        for m in _re.finditer(padrao, t, _re.I):
            linha = t[: m.start()].count("\n") + 1
            trecho = t.splitlines()[linha - 1].strip()[:78]
            falha(f"linha {linha}: {porque} -> {trecho!r}")

    # O Abstract nao tem heading proprio: `build_tcc_docx.py` extrai o bloco
    # que vem logo apos o RESUMO como texto em ingles, e o monta no
    # pre-textual do .docx — ou seja, o que esta la vai impresso. Por isso
    # uma checagem so do corpo em portugues nao pega o Abstract.
    m = _re.search(r"(?s)##\s*RESUMO(.*?)\n\*\*?Abstract\b|\*\*Abstract\b(.*)",
                   t, _re.I)
    abstrato = ""
    if m:
        abstrato = m.group(0)
    else:
        m2 = _re.search(r"(?s)Abstract\b(.{0,3000})", t)
        abstrato = m2.group(0) if m2 else ""
    if not abstrato:
        aviso("trecho do Abstract nao encontrado")
        return
    for valor, _porque in VALORES_SUBSTITUIDOS:
        if valor in abstrato:
            falha(f"ABSTRACT cita valor substituido {valor}")
    for pt, porque in PADROES_REFUTADOS:
        if _re.search(pt, abstrato, _re.I):
            falha(f"ABSTRACT repete a {porque}")
    if not _re.search(r"39[.,]426", abstrato):
        falha("ABSTRACT nao menciona a base atual (39.426)")
    if not _re.search(r"0[.,]7621", abstrato):
        falha("ABSTRACT nao menciona a acuracia atual (0,7621)")
    if not _re.search(r"0[.,]8473", abstrato):
        falha("ABSTRACT nao menciona o AUC atual (0,8473)")
    if not any("falha" in f.lower() for f in FALHAS):
        print(f"  [OK] nenhum dos {len(VALORES_SUBSTITUIDOS)} valores "
              "substituidos e nenhum dos padroes refutados")


def check_figuras_citadas(t: str) -> None:
    """Toda figura precisa ser chamada no corpo (NBR 14724).

    As seis capturas do Anexo A entram no .docx com legenda, fonte e Lista
    de Ilustrações — e nenhuma era chamada em paragrafo nenhum. A norma
    exige que toda ilustracao seja localizada no texto; uma figura so com
    legenda e lista e orfa para quem le, e a banca conta isso.
    """
    import re as _re

    i = t.find("## ANEXO A")
    if i < 0:
        i = t.find("## 5 ")
    if i < 0:
        aviso("corpo nao localizado para conferir as figuras")
        return
    corpo = t[:i]
    orfas = []
    for n in range(1, 7):
        if not _re.search(rf"Figura {n}\b", corpo):
            orfas.append(n)
    if orfas:
        falha(f"figura sem citacao no corpo (NBR 14724): {orfas}")
    else:
        print("  [OK] as 6 figuras sao citadas no corpo")


def check_fonte_figuras(t: str) -> None:
    """A fonte impressa sob cada figura não pode contradizer o Anexo A.

    A fonte vai impressa em todas as seis figuras; o Anexo A descreve como as
    capturas foram feitas. Quando os dois divergem, o documento afirma duas
    coisas incompatíveis sobre o mesmo artefato — e a fonte é a que o leitor
    vê primeiro, embaixo da figura.
    """
    import re as _re

    caminho = RAIZ / "docs" / "build_tcc_docx.py"
    if not caminho.exists():
        aviso("build_tcc_docx.py nao encontrado: fonte de figura nao conferida")
        return
    fonte_py = caminho.read_text(encoding="utf-8")
    m = _re.search(r"FONTE_IMAGENS\s*=\s*\((.*?)\)\s*\n", fonte_py, _re.S)
    if not m:
        aviso("FONTE_IMAGENS nao encontrado em build_tcc_docx.py")
        return
    fonte = " ".join(m.group(1).split())

    # O que o Anexo A afirma sobre a captura.
    if not _re.search(r"altura\s*\n?\s*ajustada|altura ajustada", t):
        falha("Anexo A nao descreve a altura ajustada da captura")
    # A fonte nao pode declarar viewport fixa, que e o que a capture refaz.
    if _re.search(r"1440\s*[x×]\s*\d+", fonte):
        falha(f"FONTE_IMAGENS declara viewport fixa, que o Anexo A nega: {fonte[:70]!r}")
    if not any("falha" in f.lower() for f in FALHAS):
        print("  [OK] FONTE_IMAGENS nao contradiz o Anexo A")


# Anglicismos de prosa. Termo tecnico legitimamente ingles (machine
# learning, random forest, dashboard, streaming, bagging, bootstrapeada,
# patch, insight quando usado como categoria) NAO entra aqui — so o que e
# editorializavel em PT-BR e aparecia no corpo.
ANGLICISMOS_PROSA: list[tuple[str, str]] = [
    ("\\brates\\b", "ingles no meio de frase em portugues"),
    ("\\bdisclaimer\\b", "anglicismo editorializavel"),
    ("\\bcaso avaliada como necess", "falta o 'seja'"),
]


def check_anglicismos(t: str) -> None:
    """Nenhum anglicismo de prosa sobrevive no corpo."""
    import re as _re

    achados = []
    for padrao, porque in ANGLICISMOS_PROSA:
        for m in _re.finditer(padrao, t, _re.I):
            ln = t[: m.start()].count("\n") + 1
            achados.append(f"linha {ln}: {m.group(0)!r} ({porque})")
    for a in achados:
        falha(a)
    if not achados:
        print(f"  [OK] nenhum dos {len(ANGLICISMOS_PROSA)} anglicismos de prosa")


def main() -> None:
    if not TEXTO.exists():
        print(f"ERRO: {TEXTO} nao existe")
        sys.exit(2)
    t = TEXTO.read_text(encoding="utf-8")

    print("1. Caracteres nao latinos")
    check_cjk(t)
    print("2. Referencias cruzadas")
    check_referencias_cruzadas(t)
    print("3. Tabelas markdown")
    check_abelas(t)
    print("4. Referencias bibliograficas")
    check_ordem_referencias(t)
    print("5. Numeros de modelo x relatorio")
    check_numeros_modelo(t)
    print("6. Quadro 1 (regioes) x banco")
    check_quadro_regioes(t)
    print("7. Dataset profissional x banco")
    check_profissional(t)
    print("8. Residuos de valores substituidos e formas refutadas")
    check_residuos(t)
    print("9. Figuras citadas no corpo (NBR 14724)")
    check_figuras_citadas(t)
    print("10. Fonte das figuras x Anexo A")
    check_fonte_figuras(t)
    print("11. Anglicismos de prosa")
    check_anglicismos(t)

    print()
    print("=" * 66)
    if AVISOS:
        print(f"{len(AVISOS)} aviso(s):")
        for a in AVISOS:
            print(f"  - {a}")
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S):")
        for f in FALHAS:
            print(f"  - {f}")
        print("VEREDITO: INCONSISTENTE")
        sys.exit(1)
    print("VEREDITO: CONSISTENTE")


if __name__ == "__main__":
    main()