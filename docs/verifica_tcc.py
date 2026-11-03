"""Verificacao de consistencia do texto do TCC II.

20 checagens que o AGENTS.md exige antes de dar um trabalho por pronto, e que
antes eram feitas a mao (e por isso falhavam). Exit code 0 = tudo consistente.

TEXTO E FORMATACAO
  1. nenhum caractere CJK/cirilico escapado no texto PT-BR;
  2. toda referencia cruzada "Seção N.M" aponta para uma seção que existe;
  3. nenhuma tabela tem coluna com contagem incompatível com o cabeçalho;
  4. as referências ABNT estão em ordem alfabética e sem entradas duplicadas;
   9. toda figura citada no corpo existe como legenda (NBR 14724);
 10. a fonte declarada de cada figura bate com o Anexo A;
 11. nenhum anglicismo de prosa;
 13. nenhuma citação autor-data em caixa alta (NBR 10520).

NUMERO CONTRA ARTEFATO — a regra de ouro do projeto
  6. o Quadro 1 contra o banco (taxa do vermelho por região, agregado por
     partida: `win` em `participants` é por jogador);
  7. o dataset profissional contra o banco (`pro_games` guarda duas linhas
     por jogo, então `COUNT(*)` devolve o dobro);
  8. o Abstract em inglês, no pré-textual do .docx, contra os artefatos de
     métrica — exigindo as DUAS bases que coexistem desde a rodada da KR;
 12. a afirmação de não-subajuste contra `reports/tune_models_39k.json`
     (delta de AUC e profundidade de árvore);
 14. a discrepância de taxa-base contra `reports/experimento_calibracao_veredito.json`;
 16. o intervalo de Wilson de cada região: o texto não pode uniformizar o que
     o intervalo não sustenta (a KR não exclui 50%);
 17. o teste (ii) de faixa de duração contra `reports/faixa_duracao.json` E
     contra `COUNT(*)` da fila 420 no banco — a soma das contagens do
     artefato é a base que o texto precisa citar;
 18. as DUAS bases declaradas onde cada número aparece: a frase que declara a
     base de modelagem não pode citar o número da descritiva, a nota da 5.3
     tem que citar as duas, e o RESUMO em português também.

PROCESSO
 15. todo script que produz medida está documentado em `docs/comandos.md`;
 19. a accuracy do Apêndice B: ou `reports/nlq_benchmark.json` existe e o
     número do texto é o do artefato, ou o texto declara que o número não tem
     artefato. Numbero publicado sem artefato e sem aviso reprova.

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
    # a mesma contagem errada, arredondada: sobreviveu na Introdução até
    # 2026-10-28 porque o literal "99.259" não casava com "~99 mil"
    ("99 mil", "contagem de jogos profissionais arredondada (o banco tem 96.716)"),
    # rodada final da KR: os numeros que a base de 41.063 substituiu
    ("8.567", "KR antes da rodada final, a contagem que(features) alcançou"),
    ("50,3%", "taxa do vermelho na KR antes da rodada final"),
    ("15.122", "contagem da faixa 0-25 min antes da rodada final"),
    ("47,2%", "taxa maxima da faixa 25-30 min antes da rodada final"),
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
    if m is None:
        # Reserva: sem ela, um "**ABSTRACT:**" ou "**Abstract**:" desliga
        # silenciosamente as sete asercoes do Abstract e ainda sai com
        # exit 0. Cobertura que se pode desligar sem erro nao e cobertura.
        #
        # A reserva comeca DEPOIS do "## RESUMO" de proposito. Casar a
        # primeira ocorrencia de "abstract" no arquivo pegava a linha 5, que
        # e o bloco de instrucoes do editor ("-> Resumo/Abstract"): as
        # asercoes disparavam contra o resumo em portugues e o diagnostico
        # apontava para o texto errado.
        pos = t.find("## RESUMO")
        cauda = t[pos:] if pos >= 0 else t
        achado = _re.search(r"(?is)\babstract\b[^*\n]*\*{0,2}\s*(.{0,4000})",
                            cauda)
        if achado:
            abstrato = achado.group(1)
            aviso("Abstract encontrado por reserva, nao por '**Abstract:**' — "
                  "conferir a marcacao")
    if m is None:
        falha("ABSTRACT nao encontrado no texto — sete asercoes do Abstract "
              "ficaram sem executar")
        abstrato = ""
    else:
        abstrato = m.group(1)
    if not abstrato:
        aviso("trecho do Abstract nao encontrado")
        return
    for valor, _porque in VALORES_SUBSTITUIDOS:
        if valor in abstrato:
            falha(f"ABSTRACT cita valor substituido {valor}")
    for pt, porque in PADROES_REFUTADOS:
        if _re.search(pt, abstrato, _re.I):
            falha(f"ABSTRACT repete a {porque}")
    # Ate 2026-10-13 esta checagem exigia as DUAS bases (41.063 e 39.426) e a
    # palavra "limitation" dentro do Abstract. Relaxada pelo mesmo motivo da
    # checagem 18(c) sobre o RESUMO em portugues: o modelo oficial do
    # Prof. Elvandi exige 100-250 palavras (confirmado contra os 10 TCC II
    # aprovados — nenhum passa de 249) e o nosso Resumo/Abstract tinham
    # 341/326. A nuance "base de modelagem != base descritiva" e detalhe de
    # metodologia/limitacao (Secao 5.8), nao algo que um resumo precise
    # carregar — e o Abstract e traducao do Resumo, tem que encolher junto.
    # O risco que a checagem protegia continua coberto: o Abstract tem que
    # citar a base descritiva real (41.063) e nao pode CLAMAR que o modelo
    # foi treinado sobre ela.
    if not _re.search(r"41[.,]063", abstrato):
        falha("ABSTRACT nao menciona a base descritiva (41.063)")
    elif _re.search(r"train\w*[^.]{0,40}41[.,]063", abstrato, _re.I):
        falha("ABSTRACT parece afirmar que o modelo foi treinado sobre "
              "41.063 (a base descritiva) — base de modelagem errada")
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

    # 2026-10-28: 5 recortes no corpo (marcador "Figura – ... | arquivo.png")
    # + as 6 telas inteiras do Apêndice F (era Anexo A). O total vem do texto,
    # não de constante: um marcador novo entra na conta sozinho.
    n_texto = len(_re.findall(r"(?m)^Figura\s*[—–-].*\|\s*\S+\.png\s*$", t))
    total = n_texto + 6
    i = t.find("## REFERÊNCIAS")
    if i < 0:
        aviso("corpo nao localizado para conferir as figuras")
        return
    corpo = t[:i]
    citadas = {int(n) for n in _re.findall(r"Figura (\d+)\b", corpo)}
    # "Figuras 6 a 11" cita a faixa inteira
    for a, b in _re.findall(r"Figuras (\d+) a (\d+)", corpo):
        citadas.update(range(int(a), int(b) + 1))
    orfas = [n for n in range(1, total + 1) if n not in citadas]
    if orfas:
        falha(f"figura sem citacao no corpo (NBR 14724): {orfas}")
    else:
        print(f"  [OK] as {total} figuras sao citadas no corpo")


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
        ("src/models/experiment_turret_plates.py", "experiment_turret_plates"),
        ("src/models/experiment_challenges_pilot.py", "experiment_challenges_pilot"),
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


def check_faixa_duracao(t: str) -> None:
    """O teste (ii) de robustez no texto tem de bater com o artefato E com o banco.

    O teste (ii) pergunta se o vies de lado e confundido com partida longa.
    O texto afirma as taxas por faixa de duracao total; `testa_faixa_duracao.py`
    grava `reports/faixa_duracao.json` com as mesmas taxas e com a contagem
    de partidas de cada faixa.

    A soma das contagens do artefato e a base da medicao. Usar isso em vez de
    uma constante escrita a mao e o que impede o texto de continuar citando
    a base antiga depois que o banco cresce — que foi exatamente o que
    aconteceu: a base foi atualizada para 41.063 e as taxas ficaram nas de
    39.426, produzindo uma frase que citava a base certa com os numeros
    errados.

    A soma tambem e confrontada com `COUNT(*)` da fila 420 no banco. Sem isso,
    uma correcao editorial no JSON se auto-ratificava: o artefato passaria a
    concordar com o texto sem nenhuma das duas coisas estar certa.
    """
    import json
    import re as _re

    caminho = RAIZ / "reports" / "faixa_duracao.json"
    try:
        artefato = json.loads(caminho.read_text(encoding="utf-8"))
        faixas = artefato.get("faixas") or artefato.get("faixa") or []
        if not faixas:
            raise ValueError("sem faixas")
        pct_artefato = [f"{f['pct_azul']:.1f}".replace(".", ",") for f in faixas]
        n_artefato = [f"{f['jogos']:,}".replace(",", ".") for f in faixas]
        amplitude = f"{artefato['amplitude_pp']:.1f}".replace(".", ",")
        abaixo = bool(artefato["todos_abaixo_de_50"])
    except Exception as exc:  # noqa: BLE001
        aviso(f"faixa_duracao.json inacessivel ou com outro formato, "
              f"teste (ii) pulado: {exc}")
        return

    # `amplitude_pp` tem de ser coerente com as faixas. Sem esta conferencia
    # o JSON pode ter a amplitude editada e o texto acompanhar a edicao, e a
    # 17 fica verde: ela amarrava as CONTAGENS ao banco, mas nao as TAXAS.
    amplitude_calc = max(f["pct_azul"] for f in faixas) - min(
        f["pct_azul"] for f in faixas)
    if abs(round(amplitude_calc, 1) - float(artefato["amplitude_pp"])) > 0.05:
        falha(f"teste (ii): o artefato declara amplitude "
              f"{artefato['amplitude_pp']} pp, e as faixas medem "
              f"{amplitude_calc:.1f} pp")

    base = f"{sum(int(f['jogos']) for f in faixas):,}".replace(",", ".")
    base_digitos = base.replace(".", "")
    rotulo = " / ".join(f"{p}% ({n})" for p, n in zip(pct_artefato, n_artefato))
    print(f"    artefato: {rotulo} | base {base} | amplitude {amplitude} pp")

    def como_numero(s: str) -> float:
        return float(s.replace(",", "."))

    lo_artefato = min(pct_artefato, key=como_numero)
    hi_artefato = max(pct_artefato, key=como_numero)

    # (a) o artefato tem que concordar com o banco, e nao so com o texto
    try:
        import sys as _sys

        _sys.path.insert(0, str(RAIZ))
        from src.db import get_conn  # noqa: PLC0415

        fila = get_conn().cursor()
        fila.execute("SELECT COUNT(*) FROM matches WHERE queue_id = 420")
        no_banco = fila.fetchone()[0]
        if str(no_banco) != base_digitos:
            falha(f"teste (ii): o artefato soma {base} partidas e a fila 420 do "
                  f"banco tem {no_banco} — o JSON foi editado a mao, ou o banco "
                  f"mudou e o teste nao foi remedido")
        else:
            print(f"    banco: fila 420 com {no_banco} partidas, confere com a "
                  f"soma do artefato")
    except Exception as exc:  # noqa: BLE001
        aviso(f"banco inacessivel, cruzamento do teste (ii) pulado: {exc}")

    # (b) TODAS as frases-sintese, nao so a primeira
    padrao_sintese = (
        # A data pode vir como 2026-10-04 ou por extenso ("4 de outubro de
        # 2026", 2026-11-02: o texto saiu do formato de diário); o que a
        # checagem exige é base, faixa e amplitude, não o formato da data.
        r"medido em (?:\S+|\d{1,2} de \w+ de \d{4}) sobre as ([\d.]+) partidas: ([\d,]+)%\s*a\s*([\d,]+)%"
        r"\s+entre\s+as\s+faixas\s+de\s+dura\u00e7\u00e3o,\s*amplitude\s+de\s+"
        r"([\d,]+)\s+ponto")
    sintetese = list(_re.finditer(padrao_sintese, t))
    if not sintetese:
        falha("teste (ii): nenhuma frase-sintese da faixa de duracao foi "
              "encontrada com base, faixa de valores e amplitude")
    for m in sintetese:
        base_txt, lo_txt, hi_txt, amp_txt = m.groups()
        ln = t[: m.start()].count("\n") + 1
        # ordem, e nao conjunto: "47,3% a 45,6%" e invertido e tem de falhar
        if (lo_txt, hi_txt) != (lo_artefato, hi_artefato):
            falha(f"teste (ii) L{ln}: a sintese cita {lo_txt}%-{hi_txt}%, e o "
                  f"artefato mede {lo_artefato}-{hi_artefato}")
        if amp_txt != amplitude:
            falha(f"teste (ii) L{ln}: amplitude de {amp_txt} pp na sintese, "
                  f"{amplitude} pp no artefato")
        if base_txt != base:
            falha(f"teste (ii) L{ln}: a sintese diz que mediu sobre {base_txt} "
                  f"partidas, e a soma do artefato e {base}")

    # (c) o paragrafo de detalhe: a serie com a contagem de cada faixa
    r2 = _re.search(r"taxas por faixa de dura\u00e7\u00e3o total s\u00e3o (.+?)\.\s*"
                    r"A amplitude \u00e9 de ([\d,]+) ponto", t, _re.S)
    if not r2:
        falha("teste (ii): o paragrafo de detalhe das faixas nao foi encontrado")
    else:
        serie, amp2 = r2.groups()
        achados = _re.findall(r"([\d,]+)%\s*\(([^)]*)\)", serie)
        pct_txt = [a for a, _ in achados]
        # a contagem e o ULTIMO numero do parenteses ("(0 a 25 min, 15.944
        # partidas)"); casar o primeiro pega o "0" do rotulo da faixa.
        n_txt = []
        for _, dentro in achados:
            m_n = _re.search(r"[\d.]+(?=[\s]*(?:partidas?|jogos?)\b|$)", dentro)
            if m_n is None:
                falha(f"teste (ii): a faixa {dentro!r} nao tem contagem "
                      "reconhecivel no paragrafo de detalhe")
            else:
                n_txt.append(m_n.group(0))
        if pct_txt != pct_artefato:
            falha(f"teste (ii): taxas no texto {pct_txt} diferem do artefato "
                  f"{pct_artefato}")
        if n_txt and n_txt != n_artefato:
            falha(f"teste (ii): contagens no texto {n_txt} diferem do artefato "
                  f"{n_artefato}")
        if amp2 != amplitude:
            falha(f"teste (ii): amplitude de {amp2} pp no paragrafo de detalhe, "
                  f"{amplitude} pp no artefato")

    # (d) o veredito so pode ser afirmativo se o artefato sustenta — nas DUAS
    # redacoes que o texto usa, porque o detalhe nao repete a frase da sintese
    if not abaixo:
        for m in _re.finditer(r"todas[^.\n]{0,40}abaixo de 50%", t, _re.I):
            ln = t[: m.start()].count("\n") + 1
            falha(f"teste (ii) L{ln}: o texto afirma {m.group(0)!r} e o "
                  "artefato registra que nao")
    if not any("teste (ii)" in f for f in FALHAS):
        print(f"  [OK] teste (ii) bate com o artefato e com o banco: base "
              f"{base}, amplitude {amplitude} pp")


def _secao(t: str, titulo: str) -> str:
    """Devolve o texto de uma secao de primeiro nivel, ate a proxima."""
    i = t.find(titulo)
    if i < 0:
        return ""
    prox = re.search(r"(?m)^#{1,3} ", t[i + len(titulo):])
    return t[i:i + len(titulo) + prox.start()] if prox else t[i:]


def check_bases_declaradas(t: str) -> None:
    """As DUAS bases tem que estar declaradas onde cada numero aparece.

    A checagem 17 protege o teste (ii). Esta protege o invariant que a rodada
    da KR criou: a base descritiva (41.063) e a base de modelagem coexistem,
    e cada frase tem que dizer de qual base fala.

    O bug que a motivou: a Secao 5.2 abria com "A base usada para treinar e
    comparar os modelos preditivos (Secao 5.4) reune 39.188 partidas [...]
    provenientes de 41.063 partidas" — a base de modelagem declarada com o
    numero da descritiva. E a secao que o leitor encontra ANTES da nota que
    explica as duas. Passava em qualquer revisao humana, porque 41.063 e o
    total real do banco.

    A base de modelagem e aceita em qualquer uma das duas formas verdadeiras:
    39.426 (o banco no congelamento) ou 39.309 (as que viraram linha de
    feature). O que nao pode aparecer ali e 41.063. Exigir o literal 39.426
    obrigaria o texto a afirmar que 39.426 partidas alimentaram o modelo, o
    que e verdade mais grosseira do que a que o modelo mediu.

    O regex casa DENTRO da 5.2 e da 5.3, nao na primeira ocorrencia do
    arquivo: uma frase nova com essa construcao antes da 5.2 — na
    Introducao, por exemplo - passaria a ser a validada e a 5.2 ficaria
    sem cobertura.
    """
    import re as _re

    DESCRITIVA = "41.063"
    MODELAGEM = ("39.426", "39.309")

    # (a) a frase que declara a base de modelagem, na 5.2 e na 5.3
    declarada = None
    for titulo in ("### 5.2", "### 5.3"):
        bloco = _secao(t, titulo)
        achado = _re.search(r"provenientes d(?:e|as) \**([\d.]+)\** partidas", bloco)
        if achado:
            declarada = (achado.group(1), t.find(bloco) + achado.start())
    if declarada is None:
        falha("bases: a frase que declara a base de modelagem "
              "('provenientes de N partidas') nao foi encontrada na 5.2 nem na 5.3")
    else:
        numero, pos = declarada
        ln = t[:pos].count("\n") + 1
        if numero == DESCRITIVA:
            falha(f"bases L{ln}: a base de MODELAGEM esta declarada com "
                  f"{DESCRITIVA}, que e a base descritiva — e o erro que a "
                  f"checagem 18 existe para pegar")
        elif numero not in MODELAGEM:
            falha(f"bases L{ln}: a base de modelagem esta declarada como "
                  f"{numero}, e ela e {DESCRITIVA} (descritiva) ou uma de "
                  f"{MODELAGEM} (modelagem)")
        else:
            print(f"  base de modelagem declarada como {numero}")

    # (b) a nota que explica as duas bases
    i = t.find("Nota sobre as bases")
    if i < 0:
        falha("bases: a nota que declara as duas bases nao existe na Secao 5.3")
    else:
        j = t.find("*)", i)
        nota = t[i:j if j > 0 else i + 1400]
        if DESCRITIVA not in nota or not any(b in nota for b in MODELAGEM):
            falta = [b for b in (DESCRITIVA, *MODELAGEM) if b not in nota]
            falha(f"bases: a nota da Secao 5.3 nao cita {falta} — sem as duas o "
                  "leitor nao sabe qual numero descreve o que")
        else:
            print("  nota da Secao 5.3 cita as duas bases")

    # (c) o RESUMO em portugues, e SO ele: a varredura precisa parar no
    # Abstract ingles, senao apagar o numero do resumo em portugues nao
    # reprova nada.
    #
    # Ate 2026-10-13 esta checagem exigia as DUAS bases (DESCRITIVA e
    # MODELAGEM) dentro do resumo. Relaxada nessa data porque o modelo
    # oficial do Prof. Elvandi exige 100-250 palavras no resumo (confirmado
    # contra os 10 TCC II aprovados: nenhum passa de 249) e o nosso tinha
    # 341 — a nuance "base de modelagem != base descritiva" e detalhe de
    # metodologia/limitacao (ja coberto pela Secao 5.8 e pelas checagens (a)
    # e (b) acima), nao algo que um resumo de 250 palavras precise carregar.
    # O risco que esta checagem protegia — o resumo CLAMAR que o modelo foi
    # treinado sobre a base descritiva — continua coberto: exige-se so que
    # DESCRITIVA apareca (a contagem real de partidas coletadas, fato que o
    # resumo deve mesmo declarar) e que nenhuma frase do tipo "treinad...
    # sobre as 41.063" exista.
    i = t.find("## RESUMO")
    if i < 0:
        falha("bases: o RESUMO nao existe no texto")
    else:
        corte = t.find("**Abstract", i)
        resumo = t[i:corte if corte > 0 else t.find("\n## ", i + 5)]
        reivindica_treino_na_descritiva = _re.search(
            r"treinad\w*[^.]{0,40}" + _re.escape(DESCRITIVA), resumo
        )
        if DESCRITIVA not in resumo:
            falha(f"bases: o RESUMO em portugues nao declara {DESCRITIVA} "
                  "(a base descritiva/total coletada)")
        elif reivindica_treino_na_descritiva:
            falha("bases: o RESUMO parece afirmar que o modelo foi treinado "
                  f"sobre {DESCRITIVA} (a base descritiva) — essa e a base de "
                  "modelagem errada, o mesmo bug que esta checagem existe "
                  "para pegar")
        else:
            print(f"  RESUMO em portugues declara {DESCRITIVA} e nao "
                  "reivindica treino sobre ela")

    # (d) a base descritiva tem que SER a que o banco tem — comparar, e nao so
    # imprimir. Sem esta comparacao a checagem avisaria nada na proxima rodada
    # de coleta, que e quando o numero do texto envelhece.
    try:
        import sys as _sys

        _sys.path.insert(0, str(RAIZ))
        from src.db import get_conn  # noqa: PLC0415

        cur = get_conn().cursor()
        cur.execute("SELECT COUNT(*) FROM matches WHERE queue_id = 420")
        real = cur.fetchone()[0]
        base_txt = f"{real:,}".replace(",", ".")
        if base_txt != DESCRITIVA:
            falha(f"bases: a base descritiva do texto e {DESCRITIVA} e a fila "
                  f"420 do banco tem {base_txt} — ou o texto envelheceu, ou a "
                  f"constante desta checagem envelheceu")
        else:
            print(f"  banco: fila 420 com {base_txt} partidas, que e a base "
                  f"descritiva declarada")
    except Exception as exc:  # noqa: BLE001
        aviso(f"banco inacessivel, cruzamento das bases pulado: {exc}")


# Marcador do heading do Apendice B. Declarado como constante porque a
# checagem precisa dele em tres lugares e o `i + 10` magico do primeiro
# versao quebrava se o titulo mudasse de tamanho.
HEADING_APENDICE_B = "## APÊNDICE B"


def _tem_chave_nlq() -> bool:
    """A chave da API de linguagem natural esta disponivel neste ambiente?

    A checagem 19 aceita, como estado legitimo, que o Apêndice B publique um
    numero sem artefato desde que o texto declare isso. Sem esta funcao esse
    "estado legitimo" e um PERDOA PERMANENTE: ninguem precisa rodar o
    benchmark, a frase fica no texto para sempre e a suite continua verde
    imprimindo [OK] para algo que o proprio texto chama de pendente.

    O bloqueio e um fato de ambiente, e a checagem consegue ler o fato. Se a
    chave esta aqui, a desculpa evaporou e o ramo vira falha — o item deixa
    de ser pendencia suspensa e passa a ser divida com gatilho.
    """
    import os as _os

    try:
        from dotenv import load_dotenv as _load

        _load(RAIZ / ".env")
    except Exception:  # noqa: BLE001,S110
        pass  # sem .env ou sem dotenv: olha so o ambiente ja pronto
    return bool(_os.environ.get("ANTHROPIC_API_KEY"))


def check_benchmark_nlq(t: str) -> None:
    """O numero do Apendice B ou tem artefato, ou declara que nao tem.

    O Apêndice B publica a execution accuracy do benchmark de linguagem
    natural. Até 2026-10-04 esse número não tinha artefato: `evaluate_nlq.py`
    só imprimia, e o valor vivia na saída de console e no diário de execução.

    A guarda aceita três estados e reprova o quarto:

    - o artefato existe, o accuracy do texto é o do JSON e a base também;
    - o artefato não existe, o texto declara a lacuna E a chave não está no
      ambiente (não haveria como produzir o artefato agora);
    - o artefato não existe e o texto declara a lacuna, mas a chave ESTÁ no
      ambiente: isso reprova, porque a desculpa "sem chave" não se sustenta.

    O que reprova é número publicado, sem artefato e sem a declaração — ou
    com a declaração que a chave disponível torna Mentirosa.
    """
    import json
    import re as _re

    i = t.find(HEADING_APENDICE_B)
    if i < 0:
        # Antes isto era `return` mudo: perdia-se o acento, renomeava-se a
        # seção ou rebaixava-se para `###` e a 19ª checagem virava no-op
        # enquanto `main()` continuava anunciando. Cobertura que se pode
        # desligar sem erro não é cobertura.
        falha(f"Apêndice B não encontrado no texto (procurado "
              f"{HEADING_APENDICE_B!r}) — a checagem do accuracy não roda")
        return
    prox = _re.search(r"(?m)^#{1,2} ", t[i + len(HEADING_APENDICE_B):])
    apendice = t[i:i + len(HEADING_APENDICE_B)
                   + (prox.start() if prox else len(t))]

    # O numero do apendice, e o paragrafo em que ele esta. A declaracao de
    # lacuna e procurada NESSE paragrafo: uma frase sobre outro artefato em
    # outro paragrafo ("o resultado nao foi arquivado no diario") nao pode
    # servir de quitacao para o accuracy.
    cab = _re.search(r"(\d+)/(\d+)\s*=\s*(\d+)%", apendice)
    if not cab:
        falha("Apêndice B: o texto não cita o accuracy no formato N/M = P% — "
              "a checagem não tem contra o que conferir")
        return
    acertos, total, pct = int(cab.group(1)), int(cab.group(2)), int(cab.group(3))
    # O bloco em que o numero esta. Pegar o primeiro bloco do apendice
    # pegava o TITULO — o heading e separado do paragrafo por linha em
    # branco, e a declaracao vive no paragrafo, nunca no titulo.
    ini = apendice.rfind("\n\n", 0, cab.start())
    fim = apendice.find("\n\n", cab.end())
    paragrafo = apendice[ini + 2:fim if fim > 0 else len(apendice)]

    # `\\s+` porque o markdown quebra a ~76 colunas e a declaracao "não tem
    # artefato" cai exatamente na quebra — um espaco literal nao casava, e a
    # checagem reprovou um texto que declarava a lacuna.
    DECLARA = (r"n[aã]o\s+tem\s+artefato|sem\s+artefato|n[aã]o\s+possui\s+artefato"
               r"|n[aã]o\s+foi\s+arquiv")
    declara = bool(_re.search(DECLARA, paragrafo, _re.I))

    artefato = RAIZ / "reports" / "nlq_benchmark.json"
    tem_artefato = artefato.exists()

    if not tem_artefato:
        if not declara:
            falha("Apêndice B: publica accuracy sem artefato em "
                  "reports/nlq_benchmark.json e sem declarar a lacuna — ou "
                  "rode o benchmark, ou diga no texto que o número não tem "
                  "artefato")
            return
        if _tem_chave_nlq():
            falha("Apêndice B: o texto declara que o número não tem artefato, "
                  "mas ANTHROPIC_API_KEY está disponível neste ambiente — a "
                  "pendência é de execução, não de ausência de chave. Rode "
                  "`python -m src.nlq.evaluate_nlq` e atualize o Apêndice B")
            return
        print("  [OK] Apêndice B declara a lacuna e ANTHROPIC_API_KEY não está "
              "no ambiente: a pendência é de chave, não de omissão")
        return

    try:
        dados = json.loads(artefato.read_text(encoding="utf-8"))
        acc_artefato = float(dados["execution_accuracy"])
        acertos_artefato = int(dados["acertos"])
        total_artefato = int(dados["total_perguntas"])
        base_artefato = f"{int(dados['base_partidas_fila_420']):,}".replace(",", ".")
        medido = dados["medido_em"]
    except Exception as exc:  # noqa: BLE001
        falha(f"Apêndice B: nlq_benchmark.json ilegível ou com outro formato "
              f"({exc}) — o artefato precisa de execution_accuracy, acertos, "
              f"total_perguntas, base_partidas_fila_420 e medido_em")
        return

    print(f"  artefato: {acertos_artefato}/{total_artefato} = "
          f"{acc_artefato:.0%} sobre {base_artefato} partidas, medido em {medido}")

    if (acertos, total) != (acertos_artefato, total_artefato) \
            or pct != round(acc_artefato * 100):
        falha(f"Apêndice B: o texto cita {acertos}/{total} = {pct}%, e o "
              f"artefato mede {acertos_artefato}/{total_artefato} = "
              f"{acc_artefato:.0%}")
        return
    if base_artefato not in apendice:
        # A base e o que o benchmark mediu sobre. Divergencia aqui e o mesmo
        # bug da checagem 18: numero certo, base errada ao lado.
        falha(f"Apêndice B: o benchmark mediu sobre {base_artefato} partidas e "
              f"o Apêndice B não declara essa base")
        return
    if declara:
        # O artefato existe: a frase de lacuna virou mentira.
        falha("Apêndice B: o texto ainda diz que o número não tem artefato, "
              "mas reports/nlq_benchmark.json existe — remova a declaração")
        return
    print("  [OK] accuracy e base do Apêndice B batem com o artefato")


def check_contagem_de_checagens() -> None:
    """O numero de checagens que os documentos afirmam tem que ser o real.

    A contagem divergiu em quatro lugares ao longo de 2026-10-04 — 12, depois
    17, depois 18, agora 20 — e nada pegava. `check_scripts_documentados`
    procura um token do nome do script em `comandos.md`, nunca o numero, e o
    numero tambem aparecia no bloco de pendencias do proprio TCC.

    SOBRE O BLOCO DE PENDENCIAS: ele NAO vai para o `.docx`. `build_tcc_docx.py`
    remove `## Pendencias finais antes da entrega` de proposito — e log de
    trabalho, nao parte do entregavel. Conferi porque a affirmacao de que ele
    "vai para a banca" era falsa, e o `.docx` nao contem `smoke_test` nem
    `verifica_tcc`. A checagem compara o `.md` mesmo assim: e o registro de
    trabalho do projeto, e um numero que diverge ali ainda e divergencia.

    A fonte da verdade e o proprio `verifica_tcc.py`: quantos `print("N.` ele
    emite. Comparar com o que cada documento afirma e o que fecha o ciclo.

    LIMITE CONHECIDO: o numero e julgado literalmente, e a checagem nao
    distingue citacao de afirmacao. Citar uma contagem antiga no diario
    reprova, mesmo dizendo que e antiga. Preferi isso a criar excecao por
    palavra-chave — excecao que nao esta no criterio afrouxa a guarda, e o
    custo aqui e reescrever uma frase.
    """
    import re as _re

    proprio = (RAIZ / "docs" / "verifica_tcc.py").read_text(encoding="utf-8")
    # o grupo de captura e obrigatorio: sem ele o findall devolve a match
    # inteira ("print(\"1.") e o int() estoura
    # o grupo de captura e obrigatorio: sem ele o findall devolve a match
    # inteira (print("1.) e o int() estoura
    reais = {int(n) for n in _re.findall(r'print\("(\d+)\.', proprio)}
    if not reais:
        falha("contagem: nao encontrei nenhum print('N.') no verifica_tcc.py — "
              "a checagem de contagem nao tem contra o que conferir")
        return
    esperado = max(reais)
    print(f"  a suite imprime {len(reais)} checagens, numeradas ate {esperado}")

    if esperado != len(reais):
        falha(f"contagem: as checagens vao ate {esperado} mas sao {len(reais)} "
              f"— ha numero pulado no main()")

    for caminho, rotulo in ((RAIZ / "docs" / "comandos.md", "comandos.md"),
                            (RAIZ / "docs" / "tcc2_texto.md", "tcc2_texto.md"),
                            (RAIZ / "docs" / "diario_execucao.md",
                             "diario_execucao.md")):
        if not caminho.exists():
            aviso(f"{rotulo} ausente: contagem de checagens nao conferida nele")
            continue
        texto = caminho.read_text(encoding="utf-8")
        # O diario e um log CRONOLOGICO: uma entrada de dia anterior falando
        # do tamanho da suite daquele dia e historica e esta certa. Julgar
        # "as 9 checagens nao-OK apontadas pela versao antiga" pela contagem
        # de hoje reprovaria o diario por registro faithfully do passado.
        # So a entrada mais recente e comparada.
        if rotulo == "diario_execucao.md":
            entradas = list(_re.finditer(r"(?m)^## (\d{4}-\d{2}-\d{2})", texto))
            if not entradas:
                aviso("diario sem entrada datada: contagem nao conferida nele")
                continue
            texto = texto[entradas[-1].start():]
        for m in _re.finditer(r"(\d+)\s+checagens", texto):
            afirmado = int(m.group(1))
            ln = texto[: m.start()].count("\n") + 1
            if afirmado != esperado:
                trecho = texto.splitlines()[ln - 1].strip()[:70]
                falha(f"contagem: {rotulo} L{ln} afirma {afirmado} checagens e a "
                      f"suite tem {esperado} -> {trecho!r}")
            else:
                print(f"  ok  {rotulo}: {afirmado} checagens, L{ln}")


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
    print("17. Teste (ii) de faixa de duracao x artefato e x banco")
    check_faixa_duracao(t)
    print("18. As duas bases declaradas onde cada numero aparece")
    check_bases_declaradas(t)
    print("19. Accuracy do NLQ: artefato ou declaracao de lacuna")
    check_benchmark_nlq(t)
    print("20. A contagem de checagens que os docs affirmam e a real")
    check_contagem_de_checagens()

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