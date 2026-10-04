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
from datetime import date
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
        # ARQUIVA a saida. O diario apontou em 2026-10-03 que a medicao
        # anterior "nao teve segunda execucao independente e a saida nao foi
        # arquivada". Sem arquivo, o Quadro 1 so tem lastro em prosa — e foi
        # assim que ele ficou com a NA1 desatualizada por duas rodadas de
        # coleta sem ninguem perceber.
        destino = RAIZ / "reports" / "stats_regions.txt"
        destino.parent.mkdir(parents=True, exist_ok=True)
        # `linhas` JÁ é usada acima para as linhas do Quadro 1 lidas do
        # texto — reutilizar o nome aqui sobrescreve e o `for` seguinte
        # desempacota a lista errada. Por isso `saida`.
        saida = [
            "VITORIA DO TIME VERMELHO POR REGIAO — fila ranqueada 420",
            f"medido em: {date.today().isoformat()}",
            "",
            "team_id = 200 (vermelho), agregado por partida antes de contar:",
            "'win' e por jogador, cinco por partida, entao a media direta sobre",
            "'participants' daria 50,0% em toda regiao por simetria.",
            "",
            f"{'regiao':<8}{'partidas':>10}{'vermelho':>12}",
        ]
        for nome, (n, p) in sorted(real.items(), key=lambda x: -x[1][0]):
            saida.append(f"{nome:<8}{n:>10}{p + '%':>12}")
        total = sum(n for n, _ in real.values())
        saida.append(f"{'TOTAL':<8}{total:>10}")
        destino.write_text("\n".join(saida) + "\n", encoding="utf-8")
        print(f"  [OK] saida arquivada em {destino.name} ({total} partidas)")
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
    # O Abstract comeca em "**Abstract:**" e termina na proxima secao de
    # primeiro nivel. A extracao anterior usava uma alternancia cujo
    # primeiro ramo casava de "## RESUMO" ate "**Abstract" — devolvia
    # o RESUMO em PORTUGUES e nunca o trecho em ingles, que e o que vai
    # para o pre-textual do .docx. Foi por isso que a checagem aceitava
    # 39.426 (que estava no RESUMO) e rejeitava 41.063: ela checava o
    # resumo, nao o abstract.
    m = _re.search(r"(?s)\*\*Abstract:?\*\*(.*?)(?=\n##\s|\Z)", t)
    abstrato = m.group(1) if m else ""
    if not abstrato:
        aviso("trecho do Abstract nao encontrado")
        return
    for valor, _porque in VALORES_SUBSTITUIDOS:
        if valor in abstrato:
            falha(f"ABSTRACT cita valor substituido {valor}")
    for pt, porque in PADROES_REFUTADOS:
        if _re.search(pt, abstrato, _re.I):
            falha(f"ABSTRACT repete a {porque}")
    # O Abstract tem que declarar AS DUAS bases. Depois da rodada final de
    # coleta da KR o banco tem 41.063 e os modelos foram construidos sobre
    # 39.426; citar so uma deixa o leitor sem saber qual numero descreve o
    # que. Exigir as duas e o que impede o Abstract de escolher o mais
    # redondo e esconder o outro.
    if not _re.search(r"41[.,]063", abstrato):
        falha("ABSTRACT nao menciona a base descritiva (41.063)")
    if not _re.search(r"39[.,]426", abstrato):
        falha("ABSTRACT nao menciona a base de modelagem (39.426) - sem ela "
              "o leitor nao sabe que os dois numeros coexistem")
    if not _re.search(r"limitation|limita", abstrato, _re.I):
        falha("ABSTRACT declara as duas bases mas nao diz que a diferenca e "
              "uma limitacao registrada")
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


def check_gridsearch(t: str) -> None:
    """A afirmação da 5.8 sobre o GridSearchCV tem que bater com o artefato.

    A 5.8 diz que a limitacao de taxa-base NAO e subajuste porque a grade
    escolheu a mesma profundidade e ficou equivalente em AUC. Durante muito
    tempo essa frase nao tinha lastro: nenhum log em reports/ a sustentava,
    e ela sobreviveu a duas rodadas de coleta sem ninguem conferir. E o
    oposto aconteceu antes — 0,7573 e 0,8393 sobreviveram ao retreino.

    Checagem de presenca nao resolve: o texto dizer "0,0001" e o relatorio
    dizer 0,0001 sao coisas diferentes. Aqui os dois sao confrontados.
    """
    import json

    rel = RAIZ / "reports" / "tune_models_39k.json"
    if not rel.exists():
        aviso("reports/tune_models_39k.json ausente: a afirmacao de nao-subajuste "
              "nao tem artefato (gere com python -m src.models.tune_models_full)")
        return
    try:
        d = json.loads(rel.read_text(encoding="utf-8"))["XGBoost"]
    except (json.JSONDecodeError, KeyError) as exc:
        falha(f"reports/tune_models_39k.json invalido: {exc}")
        return

    delta = d["delta_auc"]
    auc_prod = d["auc_producao"]
    posicao = d.get("posicao_producao_na_grade")
    mesma = d.get("mesma_profundidade")

    def num(x: float) -> str:
        return f"{x:.4f}".replace(".", ",")

    if abs(delta) >= 0.005:
        falha(f"a grade GANHA {num(delta)} de AUC sobre producao — a 5.8 nao pode "
              "afirmar que o ajuste e equivalente")
    if not mesma:
        falha(f"a grade escolheu outra profundidade; 5.8 afirma a mesma "
              f"(producao={d['producao'].get('max_depth')}, "
              f"vencedora={d['melhor_combinacao'].get('max_depth')})")
    if num(auc_prod) not in t:
        falha(f"AUC de producao ({num(auc_prod)}) medido no tuning nao esta no texto")
    # o texto tem de citar o delta com o mesmo numero de casas
    for variante in (f"{abs(delta):.4f}".replace(".", ","),
                     f"{abs(delta):.2f}".replace(".", ",")):
        if variante not in t:
            falha(f"o delta de AUC ({variante}) do tuning nao aparece no texto")
    if posicao and f"{posicao}º lugar" not in t and f"{posicao}o lugar" not in t:
        aviso(f"a posicao de producao na grade ({posicao} de 27) nao e citada "
              "no texto — o leitor nao consegue julgar o 'equivalente'")
    if not any("grade" in f.lower() or "profundidade" in f.lower() for f in FALHAS):
        print(f"  [OK] afirmacao de nao-subajuste confere com o artefato "
              f"(delta {num(delta)}, producao em {posicao}o de 27)")


def check_citacoes(t: str) -> None:
    """Citação autor-data em caixa alta viola a NBR 10520.

    Dentro de parênteses, o sobrenome vai em caixa alta e o resto em
    minúscula: "(Prodanov; Freitas, 2013)", nunca "(PRODANOV; FREITAS,
    2013)". A prosa do texto usava a forma correta — "Prodanov e Freitas
    (2013)" — e só a forma entre parênteses estava errada, o que é a pior
    mistura possível porque parece coerente.

    Três das cinco ocorrências tinham QUEBRA DE LINHA dentro do parêntese,
    que é o que fazia o casamento exato falhar. O padrão aqui aceita
    \\s+ entre os campos.
    """
    import re as _re

    padrao = _re.compile(
        r"\((?:GIL|CRESWELL|PRODANOV|FREITAS|YIN|LUND|RIBEIRO|BREIMAN|CHEN|"
        r"HANLEY|WALLNER|HODGE|JIANG|GARC)[^)]*\d{4}\)"
    )
    achados = []
    for m in padrao.finditer(t):
        # a citacao e autor-data se tem sobrenome ALFA + ano; o restante
        # em caixa alta e o defeito
        dentro = m.group(0)[1:-1]
        if _re.search(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}\b", dentro):
            ln = t[: m.start()].count("\n") + 1
            achados.append(f"linha {ln}: {m.group(0)[:44]!r} em caixa alta")
    for a in achados:
        falha(f"citacao autor-data em caixa alta (NBR 10520): {a}")
    if not achados:
        print("  [OK] nenhuma citacao autor-data em caixa alta")


def check_calibracao(t: str) -> None:
    """A conclusão da 5.8 sobre a discrepância de taxa-base tem que bater com o artefato.

    A 5.8 afirma três coisas que vieram de `experimento_calibracao.py`: que a
    calibração PIORA a discrepância, que a regularização a move dentro do
    ruído, e que só a troca de família a fecha. Cada uma é verificável contra
    `reports/experimento_calibracao_veredito.json`.

    Sem esta checagem o texto afirmaria "a calibração piora" sem que nada
    registrasse que isso foi medido — e é a afirmação mais contraintuitiva
    do trabalho, a que a banca mais vai questionar.
    """
    import json

    rel = RAIZ / "reports" / "experimento_calibracao_veredito.json"
    if not rel.exists():
        aviso("experimento_calibracao_veredito.json ausente: a afirmação da 5.8 "
              "sobre a discrepância não tem artefato")
        return
    try:
        d = json.loads(rel.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        falha(f"experimento_calibracao_veredito.json invalido: {exc}")
        return

    prod = d["producao"]
    pioram = d.get("variantes_que_pioram", [])
    fecham = d.get("variantes_que_fecham", [])

    def num(x: float) -> str:
        return f"{x:.4f}".replace(".", ",")

    # 1. a affirmacao central: nenhuma variante barata fecha
    if fecham and not d.get("alguma_variante_fecha"):
        falha("veredito contradiz a propria lista de variantes que fecham")
    # 2. a calibracao tem de estar entre as que pioram
    if not any("calib" in n for n in pioram):
        aviso("a 5.8 afirma que a calibracao piora a discrepancia, mas o "
              f"artefato lista {pioram} — confira a frase")
    # 3. os numeros citados no texto tem de existir no artefato
    for v in d.get("variantes_que_fecham", []):
        pass
    melhor = d.get("melhor_desvio")
    if melhor:
        for valor in (num(melhor["taxa_base"]), num(melhor["desvio_pp"] / 100)):
            if valor not in t and f"{melhor['desvio_pp']:.1f}".replace(".", ",") not in t:
                aviso(f"a taxa/desvio da variante que fecha ({valor}) não "
                      "aparece no texto — o leitor não consegue conferir")
        print(f"  [OK] variante que fecha: desvio {melhor['desvio_pp']:.1f} pp, "
              f"AUC {num(melhor['auc'])}")


def check_regioes_significativas(t: str) -> None:
    """Nenhuma região pode ser declarada pendente sem teste estatístico.

    A Seção 5.3 afirmava que "as QUATRO regiões com amostra relevante
    PENDEM para o vermelho, entre 50,3% e 56,3%". A KR fica em 50,3% com
    intervalo de Wilson de 95% em [49,2%, 51,3%] — que INCLUI 50%. Na KR o
    viés não é distinguível de zero, e "pende" está errado.

    Isto é mais grave que os outros números corrigidos nesta rodada: é a
    sustentação da generalização do achado. A pergunta "o viés é do elo alto
    ou é do Brasil?" se responde pela consistência entre regiões, e a KR é
    justamente a que não sustenta a resposta.

    A checagem calcula os intervalos e falha se o texto afirmar uniforme
    quando o dado não é.
    """
    import math
    import re as _re

    try:
        import sys

        sys.path.insert(0, str(RAIZ))
        from src.db import get_conn  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        aviso(f"banco inacessivel,ICs por regiao pulados: {exc}")
        return

    def wilson(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
        p = x / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - m, c + m

    try:
        cur = get_conn().cursor()
        # team_id 200 = vermelho, agregado por partida: `win` é por jogador
        cur.execute(
            """
            SELECT split_part(match_id,'_',1), COUNT(*),
                   SUM(CASE WHEN v_red > 0 THEN 1 ELSE 0 END)
            FROM (SELECT match_id, SUM(CASE WHEN win THEN 1 ELSE 0 END) AS v_red
                  FROM participants WHERE team_id = 200 GROUP BY match_id) t
            GROUP BY 1 HAVING COUNT(*) > 100
            """
        )
        regioes = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    except Exception as exc:  # noqa: BLE001
        aviso(f"consulta regional falhou: {exc}")
        return

    nao_signif = []
    for nome, (n, v) in sorted(regioes.items()):
        lo, hi = wilson(v, n)
        firme = (lo * 100 > 50) or (hi * 100 < 50)
        if not firme:
            nao_signif.append(nome)
        marca = "exclui 50%" if firme else "**inclui 50%**"
        print(f"    {nome:<6} {100*v/n:>5.1f}%  IC [{lo*100:.1f}%, {hi*100:.1f}%]  {marca}")

    if not nao_signif:
        print("  [OK] todas as regiões com amostra suficiente excluem 50%")
        return

    # Se alguma região não é significativa, o texto não pode dizer que todas
    # "pendem" nem que a direção é "consistente nas quatro" sem qualificar.
    uniforme = _re.findall(
        r"as quatro regi\u00f5es[^.]*pendem|"
        r"dire\u00e7\u00e3o\s+consistente nas quatro regi\u00f5es|"
        r"as quatro regi\u00f5es com amostra relevante pendem",
        t, _re.I)
    if uniforme:
        for m in uniforme:
            falha(f"texto afirma as quatro regioes de forma uniforme, mas "
                  f"{nao_signif} nao exclui 50%: {m[:64]!r}")
    # E a ressalva tem de estar presente, com o número da região culpada.
    if not any(r in t for r in nao_signif) or "inclui 50%" not in t:
        falha(f"nenhuma ressalva no texto de que {nao_signif} tem intervalo "
              "que inclui 50%")
    if not any("KR" in f for f in FALHAS):
        print(f"  [OK] texto qualifica: {nao_signif} tem IC que inclui 50%")


def check_scripts_documentados() -> None:
    """Todo script executável do projeto tem de estar em `docs/comandos.md`.

    Esta checagem existe porque o padrão se repetiu duas vezes: no Bloco A
    do plano de fechamento documentei os 9 scripts que existiam naquele
    momento, e depois criei mais 3 (`testa_faixa_duracao`,
    `experimento_calibracao`, `reavalia_calibracao`) sem documentar nenhum.
    O `AGENTS.md` chama documentação divergente do código de bug, e a
    divergência foi exatamente essa.

    Escopo: scripts que produzem medida ou artefato. Um utilitário interno
    não entra, e por isso a lista de exceções é explícita e não um filtro
    por nome de arquivo.
    """
    import re as _re

    # (caminho, está em comandos.md)
    alvos = [
        ("src/models/multi_cutoff_metrics.py", "multi_cutoff_metrics"),
        ("src/models/tune_models_full.py", "tune_models_full"),
        ("docs/verifica_tcc.py", "verifica_tcc"),
        ("docs/confere_docx.py", "confere_docx"),
        ("docs/recapturar_anexo_a.py", "recapturar_anexo_a"),
        ("docs/taxa_base_por_corte.py", "taxa_base_por_corte"),
        ("docs/testa_diferenca_taxas.py", "testa_diferenca_taxas"),
        ("docs/confere_conversao_advantagem.py", "confere_conversao_advantagem"),
        ("docs/testa_faixa_duracao.py", "testa_faixa_duracao"),
        ("docs/experimento_calibracao.py", "experimento_calibracao"),
        ("docs/reavalia_calibracao.py", "reavalia_calibracao"),
    ]
    doc = RAIZ / "docs" / "comandos.md"
    if not doc.exists():
        aviso("docs/comandos.md ausente: cobertura dos scripts nao conferida")
        return
    texto = doc.read_text(encoding="utf-8")

    faltando, inexistente = [], []
    for caminho, token in alvos:
        if not (RAIZ / caminho).exists():
            inexistente.append(caminho)
            continue
        if token not in texto:
            faltando.append(f"{caminho} (procure por `{token}`)")

    for f in faltando:
        falha(f"script existe mas nao esta em docs/comandos.md: {f}")
    for c in inexistente:
        falha(f"docs/comandos.md cita um script que nao existe: {c}")
    if not faltando and not inexistente:
        print(f"  [OK] os {len(alvos)} scripts que produzem medida estao "
              "documentados em comandos.md")


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
    print("12. Afirmacao de nao-subajuste x artefato do tuning")
    check_gridsearch(t)
    print("13. Citacoes autor-data em caixa alta (NBR 10520)")
    check_citacoes(t)
    print("14. Discrepancia de taxa-base x artefato do experimento")
    check_calibracao(t)
    print("15. Scripts que produzem medida estao em comandos.md")
    check_scripts_documentados()
    print("16. Regioes: o texto nao pode uniformizar o que o IC nao sustenta")
    check_regioes_significativas(t)

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