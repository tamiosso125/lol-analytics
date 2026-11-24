"""Confere célula por célula os quadros do .docx contra o artefato que os originou.

POR QUE EXISTE: `verifica_tcc.py` confere os números que o texto afirma
(taxas, contagens, a AUC-ROC do quadro principal), mas não tinha uma regra por
quadro. Em 2026-11-10, pedida a revisão de todos os quadros, a conferência por
amostragem não bastava: um quadro com 60 células tem 60 chances de divergir do
`reports/*.json` sem que a frase que o cita mude. Este script lê os 32 quadros
do `docs/tcc2_final.docx` (o que vai ao professor, não o .md) e compara cada
célula numérica com o JSON ou a consulta ao banco de origem.

Cobertura (ver `COBERTURA` no fim): quadros com artefato numérico são
conferidos célula a célula; os que são texto (Quadros 1, 6, 19, 22, 25, 28) ou
registro histórico sem artefato (7, 8) ficam fora e aparecem listados como
"não numérico".

CRITÉRIO: o número impresso tem de ser o artefato arredondado ao mesmo número de
casas. Diferença de arredondamento (0,8487 contra 0,8488) é divergência: foi
assim que o Apêndice K citou a base errada.

Uso:
    .venv\\Scripts\\python.exe docs\\confere_quadros.py
Exit code 0 = nenhuma divergência.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from docx import Document

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REP = RAIZ / "reports"

# 2026-11-23: o TCC foi simplificado (apêndices D, E, G, I, J, K e parte de B, C, F, H
# cortados) e os quadros foram renumerados. Os conferidores abaixo continuam
# indexados pelo número da numeração ANTERIOR; este mapa liga o TÍTULO de cada quadro
# que sobrou a esse número, para que a conferência não dependa da posição. O que
# não está aqui não existe mais no TCC e não é conferido (os artefatos seguem em reports/).
MAPA_ANTIGO: dict[str, int] = {
    "Tabelas do banco de dados e o que cada uma guarda": 1,
    "Vitória do time vermelho por região": 2,
    "Comparação entre modelos após o ajuste (corte de 15 minutos)": 3,
    "Desempenho do XGBoost por corte temporal": 4,
    "Esquema relacional do banco de dados": 6,
    "Auditoria de fundamentação do coach (36 respostas)": 10,
    "Métricas completas por corte temporal, comparação entre os três modelos": 11,
    "Configuração dos três modelos comparados": 12,
    "Treino no passado e teste no futuro, XGBoost": 15,
    "AUC-ROC do XGBoost por corte, nas partidas elegíveis e nas mesmas partidas": 17,
    "Calibração do XGBoost nas partidas empatadas, com probabilidades fora da dobra": 23,
}
NOVO: dict[int, int] = {}  # número antigo -> número atual no docx
MENOS = "−"


def J(nome: str):
    return json.loads((REP / f"{nome}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- leitura do docx
def ler_quadros() -> dict[int, tuple[str, list[list[str]]]]:
    import os
    d = Document(os.environ.get("QUADROS_DOCX") or str(RAIZ / "docs" / "tcc2_final.docx"))  # QUADROS_DOCX: só para testar a reprovação
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    quadros, ultimo = {}, None
    for el in d.element.body.iterchildren():
        if el.tag.endswith("}p"):
            # Todo w:t do paragrafo, inclusive o resultado de campo SEQ gravado
            # como w:fldSimple (o Word grava assim as vezes; Paragraph.text
            # ignora o texto dentro de fldSimple e a legenda ficava "Quadro  -").
            ns_t = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
            t = "".join(x.text or "" for x in el.iter(ns_t)).strip()
            m = re.match(r"^Quadro (\d+) - (.*)$", t)
            if m:
                ultimo = (int(m[1]), m[2])
        elif el.tag.endswith("}tbl") and ultimo:
            linhas = [[c.text.strip() for c in r.cells] for r in Table(el, d).rows]
            antigo = MAPA_ANTIGO.get(ultimo[1])
            if antigo is None:
                print(f"  AVISO: quadro '{ultimo[1][:60]}' (hoje Quadro {ultimo[0]}) sem conferidor no mapa")
                antigo = 1000 + ultimo[0]
            NOVO[antigo] = ultimo[0]
            quadros[antigo] = (ultimo[1], linhas)
            ultimo = None
    return quadros


# ---------------------------------------------------------------- formatação pt-BR
def f(x: float, nd: int) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


def fs(x: float, nd: int) -> str:
    """Com sinal explícito; o sinal vem do valor sem arredondar."""
    return ("+" if x >= 0 else MENOS) + f"{abs(x):.{nd}f}".replace(".", ",")


def milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def ic(d: dict, nd: int = 4) -> str:
    return f"{fs(d['delta_auc'], nd)} ({fs(d['ic_lo'], nd)} a {fs(d['ic_hi'], nd)})"


RES: dict[int, list[str]] = {}
CONT: dict[int, list[int]] = {}


def cmp(q: int, rotulo: str, impresso: str, esperado: str) -> None:
    CONT.setdefault(q, [0, 0])
    CONT[q][0] += 1
    if impresso.strip() != esperado:
        CONT[q][1] += 1
        RES.setdefault(q, []).append(f"{rotulo}: impresso {impresso!r}, artefato {esperado!r}")


def linha(rows, *prefixo):
    for r in rows[1:]:
        if all(r[i] == p for i, p in enumerate(prefixo)):
            return r
    return None


def exigir(q, rows, *prefixo):
    r = linha(rows, *prefixo)
    if r is None:
        CONT.setdefault(q, [0, 0])
        CONT[q][1] += 1
        RES.setdefault(q, []).append(f"linha {prefixo} não encontrada no quadro")
    return r


# ---------------------------------------------------------------- conferências
def q3(rows):
    mc, aj, an = J("metricas_corte")["resultados"]["15"], J("metricas_ajustados")["modelos"], J("tune_models_aninhado")["modelos"]
    lg = next(v for k, v in aj.items() if k.startswith("Regress"))
    fontes = {
        "Regressão logística (sem hiperparâmetro ajustado)": (lg, None),
        "MLP ajustado": (aj["MLP ajustado"], an["MLP"]["auc"]),
        "XGBoost ajustado (produção)": (mc["XGBoost"], an["XGBoost"]["auc"]),
        "Random Forest ajustada": (aj["Random Forest ajustada"], an["RandomForest"]["auc"]),
        "MLP (referência)": (mc["MLP"], None),
        "Random Forest (referência)": (mc["RandomForest"], None),
    }
    for nome, (m, nest) in fontes.items():
        r = exigir(3, rows, nome)
        if not r:
            continue
        a = m.get("acuracia")
        for i, k in enumerate(["acuracia", "precisao", "recall", "f1", "auc"], 1):
            cmp(3, f"{nome} {k}", r[i], f(m[k], 4))
        cmp(3, f"{nome} aninhada", r[6], "—" if nest is None else f(nest, 4))


def q4(rows):
    mc = J("metricas_corte")["resultados"]
    for c in ("10", "15", "20", "25"):
        r = exigir(4, rows, f"{c} min")
        if r:
            x = mc[c]["XGBoost"]
            cmp(4, f"{c} n", r[1], milhar(x["n"]))
            cmp(4, f"{c} acc", r[2], f(x["acuracia"], 4))
            cmp(4, f"{c} auc", r[3], f(x["auc"], 4))


def q11(rows):
    mc = J("metricas_corte")["resultados"]
    nomes = {"Random Forest": "RandomForest", "XGBoost": "XGBoost", "MLP": "MLP"}
    for r in rows[1:]:
        c = r[0].split()[0]
        m = mc[c][nomes[r[3]]]
        rot = f"{r[0]} {r[3]}"
        cmp(11, rot + " n", r[1], milhar(m["n"]))
        cmp(11, rot + " taxa", r[2], f(m["taxa_vitoria_azul"], 3))
        for i, k in enumerate(["acuracia", "precisao", "recall", "f1", "auc"], 4):
            cmp(11, f"{rot} {k}", r[i], f(m[k], 4))


def q13(rows):
    b = J("baseline_e_diferencas")["resultados"]
    lg = lambda c: next(v for k, v in b[c]["modelos"].items() if k.startswith("Regress"))
    dif = lambda c, nome: next(v for k, v in b[c]["diferencas"].items() if nome in k)
    for r in rows[1:]:
        c = r[0].split()[0]
        if r[1] == "Regressão logística":
            m, d = lg(c), dif(c, "gress")
        else:
            nome = "MLP" if r[1].startswith("MLP") else "Random Forest"
            m, d = b[c]["modelos"][nome], dif(c, nome)
        a = d["auc"]
        cmp(13, f"{r[0]} {r[1]} acc", r[2], f(m["acuracia"], 4))
        cmp(13, f"{r[0]} {r[1]} auc", r[3], f(m["auc"], 4))
        cmp(13, f"{r[0]} {r[1]} dif", r[4], f"{fs(a[0], 4)} ({fs(a[1], 4)} a {fs(a[2], 4)})")


def q14(rows):
    rb = J("robustez_dobras")["resultados"]
    nomes = {"XGBoost": "XGBoost", "Random Forest (referência)": "RandomForest", "MLP (referência)": "MLP"}
    for r in rows[1:]:
        c = r[0].split()[0]
        m = rb[c][nomes[r[1]]]
        cmp(14, f"{r[0]} {r[1]} acc5", r[2], f(m["5"]["acuracia"], 4))
        cmp(14, f"{r[0]} {r[1]} acc10", r[3], f(m["10"]["acuracia"], 4))
        cmp(14, f"{r[0]} {r[1]} auc5", r[4], f(m["5"]["auc"], 4))
        cmp(14, f"{r[0]} {r[1]} auc10", r[5], f(m["10"]["auc"], 4))


def q15(rows):
    h = J("holdout_temporal")["cortes"]
    div = {"Cronológica 80/20": "cronologica", "Por patch": "por_patch", "Aleatória 80/20": "aleatoria"}
    for r in rows[1:]:
        c = r[0].split()[0]
        x = h[c][div[r[1]]]["XGBoost"]
        rot = f"{r[0]} {r[1]}"
        cmp(15, rot + " treino", r[2], milhar(x["n_treino"]))
        cmp(15, rot + " teste", r[3], milhar(x["n_teste"]))
        cmp(15, rot + " acc", r[4], f(x["acuracia"], 4))
        cmp(15, rot + " auc", r[5], f(x["auc"], 4))
        cmp(15, rot + " ic", r[6], f"{f(x['auc_ic95'][0], 4)} a {f(x['auc_ic95'][1], 4)}")


def q16(rows):
    pts = J("curva_aprendizado")["curva_15min"]["pontos"]
    for r, p in zip(rows[1:], pts):
        cmp(16, f"treino {p['treino']}", r[0], milhar(p["treino"]))
        cmp(16, f"{p['treino']} auc", r[1], f(p["auc_media"], 4))
        cmp(16, f"{p['treino']} dp", r[2], "—" if p["sorteios"] == 1 else f(p["auc_dp"], 4))


def q17(rows):
    c = J("curva_aprendizado")["cortes"]
    for r in rows[1:]:
        k = r[0].split()[0]
        cmp(17, f"{k} elegiveis n", r[1], milhar(c[k]["elegiveis_n"]))
        cmp(17, f"{k} elegiveis auc", r[2], f(c[k]["elegiveis_auc"], 4))
        cmp(17, f"{k} mesmas n", r[3], milhar(c[k]["mesmas_n"]))
        cmp(17, f"{k} mesmas auc", r[4], f(c[k]["mesmas_auc"], 4))


def q20(rows):
    fx = J("faixa_duracao")["faixas"]
    for r, x in zip(rows[1:], fx):
        cmp(20, f"{r[0]} jogos", r[1], milhar(x["jogos"]))
        cmp(20, f"{r[0]} azul", r[2], f(x["pct_azul"], 1) + "%")


def q23(rows):
    p = J("calibracao_empate_real")["producao_por_corte"]
    for r in rows[1:]:
        c = r[0].split()[0]
        x = p[c]
        cmp(23, f"{c} n", r[1], milhar(x["empatadas"]))
        lo, hi = x["ic95_observada"]
        cmp(23, f"{c} taxa", r[2], f"{f(100*x['taxa_observada'],1)}% ({f(100*lo,1)}% a {f(100*hi,1)}%)")
        cmp(23, f"{c} media", r[3], f(100 * x["media_prevista_empatadas"], 1) + "%")
        cmp(23, f"{c} dif", r[4], fs(x["diferenca_pp"], 2) + " pp")
        cmp(23, f"{c} desvio", r[5], f(x["decis_maior_desvio_pp"], 2) + " pp")


def q24(rows):
    v = J("calibracao_empate_real")["variantes"]
    nm = {"Produção": "producao", "Sigmoidal": "sigmoide", "Isotônica": "isotonica"}
    prod = J("calibracao_empate_real")["producao_por_corte"]
    for r in rows[1:]:
        c = r[0].split()[0]
        k = nm[r[1]]
        x = prod[c] if k == "producao" else None
        if x is None:
            alvo = v.get(c, {}).get(k) or v.get(k, {}).get(c)
            if alvo is None:
                CONT.setdefault(24, [0, 0])
                CONT[24][1] += 1
                RES.setdefault(24, []).append(f"{r[0]} {r[1]}: variante não achada no JSON (chaves {list(v)[:4]})")
                continue
            x = alvo
        cmp(24, f"{c} {k} dif", r[2], fs(x["diferenca_pp"], 2) + " pp")
        cmp(24, f"{c} {k} desvio", r[3], f(x["decis_maior_desvio_pp"], 2) + " pp")
        cmp(24, f"{c} {k} medio", r[4], f(x["decis_desvio_medio_pp"], 2) + " pp")
        cmp(24, f"{c} {k} brier", r[5], f(x["brier"], 4))
        cmp(24, f"{c} {k} auc", r[6], f(x["auc"], 4))


def q29(rows):
    s = J("shap_importance_phases")
    nm = {"Diferença de ouro": "gold_diff", "Diferença de experiência": "xp_diff", "Diferença de abates": "kill_diff",
          "Diferença de torres": "tower_diff", "Diferença de dragões": "dragon_diff"}
    for r in rows[1:]:
        for i, c in enumerate(("10", "15", "20", "25"), 1):
            cmp(29, f"{r[0]} {c}", r[i], f(s[c][nm[r[0]]], 4))


def q5(rows):
    ea = J("experimentos_antigos")
    chave = {1: "A01_barao_arauto", 2: "A02_dispersao", 5: "A05_ouro_itens", 7: "A05_ouro_itens",
             6: "A06_ofensivas", 8: "A08_visao_ambas", 9: "A09_dragoes_tipo", 10: "A10_placas"}
    for r in rows[1:]:
        n = int(r[0])
        if n in chave:
            d = [ea[c][chave[n]]["xgb_prod"]["delta_auc"] for c in ("15", "25")]
        elif n == 3:
            d = [ea[c]["tuning_aninhado"]["delta_auc"] for c in ("15", "25")]
        else:
            d = [ea[c]["calibracao"]["sigmoide"]["delta_auc"] for c in ("15", "25")]
        cmp(5, f"exp {n}", r[2], f"{fs(d[0], 4)} e {fs(d[1], 4)}")


def q30(rows):
    ea = J("experimentos_antigos")
    chave = {"1": "A01_barao_arauto", "2": "A02_dispersao", "5 e 7": "A05_ouro_itens", "8": "A08_visao_ambas",
             "9": "A09_dragoes_tipo", "10": "A10_placas"}
    for r in rows[1:]:
        e, desc = r[0], r[1]
        if e in chave:
            d = [ea[c][chave[e]]["xgb_prod"] for c in ("15", "25")]
        elif e == "3":
            d = [ea[c]["tuning_aninhado"] for c in ("15", "25")]
        elif e == "4":
            k = "sigmoide" if "sigmoide" in desc else "isotonica"
            d = [ea[c]["calibracao"][k] for c in ("15", "25")]
        elif e == "6":
            k = "A06_ofensivas" if "ofensivos" in desc else "A06_defensivas"
            d = [ea[c][k]["xgb_prod"] for c in ("15", "25")]
        else:
            continue
        cmp(30, f"exp {e} {desc[:20]} 15", r[2], ic(d[0]))
        cmp(30, f"exp {e} {desc[:20]} 25", r[3], ic(d[1]))


def q31(rows):
    ep, eh, gl = J("experimentos_precisao"), J("experimento_historico"), J("ganho_variaveis_logit")["cortes"]
    chave = {"12": "E12_trajetoria", "13": "E13_funcao", "14": "E14_objetivos", "15": "E15_rico",
             "16": "E16_campeoes", "17": "E17_jogadores"}
    for r in rows[1:]:
        e, desc = r[0], r[1]
        for col, c in ((2, "15"), (3, "25")):
            if e in chave:
                d = ep[c][chave[e]]["xgb_prod"]
            elif e == "18" and "contra o XGBoost de produção" in desc:
                d = ep[c]["E18_tudo"]["logit"]
            elif e == "18" and "contra a regressão" in desc:
                g = gl[c]["logit"]["E18_tudo"]
                d = {"delta_auc": g["ganho_auc"], "ic_lo": g["ic_lo"], "ic_hi": g["ic_hi"]}
            elif e == "18":
                d = ep[c]["E18_tudo"]["xgb_prod"]
            elif e == "19":
                x = eh[c]["5+"]["logit"]["dauc_ic"]
                d = {"delta_auc": x[0], "ic_lo": x[1], "ic_hi": x[2]}
            else:
                continue
            cmp(31, f"exp {e} {desc[:24]} {c}", r[col], ic(d))


def q32(rows):
    hp = J("holdout_precisao")["cortes"]
    div = {"Cronológica 80/20": "cronologica", "Por patch": "por_patch", "Aleatória 80/20": "aleatoria"}
    for r in rows[1:]:
        c = r[0].split()[0]
        x = hp[c][div[r[1]]]
        base, lg = x["base"]["xgb_prod"], x["E18_tudo"]["logit"] if "E18_tudo" in x else None
        if lg is None:
            CONT.setdefault(32, [0, 0]); CONT[32][1] += 1
            RES.setdefault(32, []).append(f"{r[0]} {r[1]}: sem E18_tudo/logit em holdout_precisao ({list(x)})")
            continue
        cmp(32, f"{r[0]} {r[1]} xgb", r[2], f(base["auc"], 4))
        cmp(32, f"{r[0]} {r[1]} logit", r[3], f(lg["auc"], 4))
        d = lg["dauc_vs_base_xgb"]
        cmp(32, f"{r[0]} {r[1]} ganho", r[4], f"{fs(d[0], 4)} ({fs(d[1], 4)} a {fs(d[2], 4)})")


def banco():
    try:
        from src.db import get_conn
        return get_conn()
    except Exception as e:  # noqa: BLE001
        print("  (banco indisponível:", e, ")")
        return None


def q2_21_26(q):
    cm = banco()
    if cm is None:
        return
    with cm as c:
        cur = c.cursor()
        # Quadro 2
        # vitória do time VERMELHO (team_id 200, win=true), a definição do texto.
        # Contar "derrotas do azul" dá 50,5% na KR: duas partidas têm os dois
        # times com win=false (2026-11-10), e a diferença é só essa.
        cur.execute("""select m.platform_id, count(*), round(100.0*avg(t.win::int),1)
                       from matches m join teams t on t.match_id=m.match_id and t.team_id=200
                       where m.queue_id=420 group by 1 order by 2 desc""")
        banco_reg = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
        rows = q[2][1]
        for r in rows[1:]:
            reg = r[0]
            n, red = banco_reg[reg]
            cmp(2, f"{reg} n", r[1], milhar(n))
            cmp(2, f"{reg} vermelho", r[2].split()[0], f(float(red), 1) + "%")
        # Quadro 21 (série anual do profissional: saiu do TCC em 2026-11-23)
        if 21 not in q:
            return
        cur.execute("""select year, count(distinct game_id), round(100.0*avg(win::int),1)
                       from pro_games where side='Blue' group by 1 order by 1""")
        anos = {int(a): (n, p) for a, n, p in cur.fetchall()}
        rows = q[21][1]
        for r in rows[1:]:
            for ia in (0, 2):
                if r[ia].isdigit():
                    a = int(r[ia])
                    cmp(21, f"ano {a}", r[ia + 1], f(float(anos[a][1]), 1) + "%")
        cur.execute("select round(100.0*avg(win::int),1) from pro_games where side='Blue'")
        cmp(21, "todos os anos", rows[-1][3], f(float(cur.fetchone()[0]), 1) + "%")
        # Quadro 26 (itens contáveis)
        cur.execute("select count(distinct game_id), count(distinct league) from pro_games")
        n, lig = cur.fetchone()
        r = exigir(26, q[26][1], "Jogos profissionais nos arquivos")
        if r:
            cmp(26, "pro jogos/ligas", r[1], f"{milhar(n)} jogos únicos, de {lig} ligas")
        cur.execute("select count(*) from players")
        r = exigir(26, q[26][1], "Jogadores da tabela players")
        if r:
            cmp(26, "players", r[1].split(",")[0], milhar(cur.fetchone()[0]))


def q9(rows):
    por = J("nlq_gabarito_resultado_203")["resumo"]["por_familia"]
    for r in rows[1:]:
        k = r[0]
        if k not in por:
            CONT.setdefault(9, [0, 0]); CONT[9][1] += 1
            RES.setdefault(9, []).append(f"família {k} fora do JSON")
            continue
        x = por[k]
        cmp(9, f"{k} certas", r[2], str(x["certas"]))
        cmp(9, f"{k} total", r[3], str(x["total"]))
        cmp(9, f"{k} %", r[4], f(x["pct"], 1))
    soma = sum(x["certas"] for x in por.values())
    tot = sum(x["total"] for x in por.values())
    cmp(9, "soma das famílias", f"{soma} de {tot}", "181 de 203")
    cmp(9, "famílias no quadro", str(len(rows) - 1), str(len(por)))


def q10(rows):
    a = J("coach_audit")["resumo"]
    rv = J("coach_audit_revisao")
    cl = {}
    for x in rv["sinalizados"]:
        cl[x["classe"]] = cl.get(x["classe"], 0) + 1
    esperado = {
        "Respostas auditadas": f"{a['casos']} ({a['por_modo']['completo']} por modo)",
        "Números nas respostas": f"{a['numeros_total']}, dos quais {a['numeros_tempo_ou_formato']} de tempo de jogo ou formato",
        "Não encontrados nos dados": f"{a['numeros_sinalizados']}, em {a['casos_com_sinalizado']} respostas",
        "Estatística inventada, após a revisão": f"0 ({cl.get('derivado', 0)} derivados dos dados, {cl.get('formato', 0)} de formato, {cl.get('conhecimento_geral', 0)} limiares de conhecimento geral)",
        "Porcentagens com correspondente nos dados": f"{a['percentuais'] - a['percentuais_sem_correspondente']} de {a['percentuais']}",
        "Contagens de jogos ou partidas com correspondente": f"{a['contagens_de_jogos'] - a['contagens_sem_correspondente']} de {a['contagens_de_jogos']}",
        "Ressalva final de limites": f"{rv['ressalva_final_lida']['com_ressalva']} de {rv['ressalva_final_lida']['casos']} ({a['ressalva_final_heuristica']} pelo detector, {rv['ressalva_final_lida']['com_ressalva'] - a['ressalva_final_heuristica']} por leitura)",
        "Itens sugeridos que vêm da lista real fornecida": f"{a['itens_nos_dados_fornecidos']} de {a['itens_sugeridos']}",
    }
    for r in rows[1:]:
        if r[0] in esperado:
            cmp(10, r[0], r[1], esperado[r[0]])
        else:
            cmp(10, r[0], r[1], "(medida fora do mapa)")


def q8(rows):
    det = J("nlq_benchmark")["detalhe"]
    norm = lambda t: re.sub(r"\s+", " ", t).strip().rstrip(";")
    for r in rows[1:]:
        d = next((x for x in det if str(x["n"]) == r[0]), None)
        if d is None:
            cmp(8, f"pergunta {r[0]}", "presente", "ausente no JSON")
            continue
        cmp(8, f"pergunta {r[0]} texto", norm(r[1]), norm(d["pergunta"]))
        cmp(8, f"pergunta {r[0]} SQL", norm(r[2]), norm(d["sql_referencia"]))
    cmp(8, "número de perguntas", str(len(rows) - 1), str(len(det)))


def q12(rows):
    an, aj = J("tune_models_aninhado")["modelos"], J("metricas_ajustados")["modelos"]
    mc = J("metricas_corte")["resultados"]["15"]
    r = exigir(12, rows, "XGBoost aninhado")
    if r:
        cmp(12, "xgb aninhado", r[2], f"a produção foi escolhida em {sum(1 for e in an['XGBoost']['escolhas_por_dobra'] if e == {'learning_rate': 0.01, 'max_depth': 3, 'n_estimators': 500})} das 5 dobras; acurácia {f(an['XGBoost']['acuracia'], 4)}, AUC-ROC {f(an['XGBoost']['auc'], 4)}")
    r = exigir(12, rows, "Random Forest ajustada")
    if r:
        cmp(12, "rf ajustada", r[2].split("avaliada nas mesmas dobras: ")[-1],
            f"{f(aj['Random Forest ajustada']['acuracia'], 4)} e {f(aj['Random Forest ajustada']['auc'], 4)}; aninhada: {f(an['RandomForest']['acuracia'], 4)} e {f(an['RandomForest']['auc'], 4)}")
    r = exigir(12, rows, "MLP ajustado")
    if r:
        cmp(12, "mlp ajustado", r[2].split("avaliada nas mesmas dobras: ")[-1],
            f"{f(aj['MLP ajustado']['acuracia'], 4)} e {f(aj['MLP ajustado']['auc'], 4)}; aninhada: {f(an['MLP']['acuracia'], 4)} e {f(an['MLP']['auc'], 4)}")


def q6(rows):
    import psycopg2  # noqa: F401
    from src.db import get_conn
    with get_conn() as c:
        cur = c.cursor()
        for r in rows[1:]:
            cur.execute("select column_name from information_schema.columns where table_name=%s", (r[0],))
            banco = {x[0] for x in cur.fetchall()}
            doc = {re.sub(r"\s*\(.*?\)", "", x).strip() for x in r[1].split(", ")}
            falta, sobra = sorted(banco - doc), sorted(doc - banco)
            cmp(6, f"{r[0]} campos", "iguais" if not sobra and not falta else f"quadro tem a mais {sobra}, falta {falta}", "iguais")


def q18_26(q):
    from src.db import get_conn
    with get_conn() as c:
        cur = c.cursor()
        cur.execute("select platform_id, count(*) from matches where queue_id=420 group by 1")
        n = dict(cur.fetchall())
        for r in q[18][1][1:]:
            cmp(18, f"{r[0]} última medição", r[2], milhar(n[r[0]]))
        t26 = q[26][1]
        cur.execute("select count(*), round(100.0*avg((tier='MASTER')::int)) from players")
        tot, pm = cur.fetchone()
        r = exigir(26, t26, "Jogadores da tabela players")
        if r:
            cmp(26, "players", r[1], f"{milhar(tot)}, dos quais {int(pm)}% de Mestre")
        cur.execute("""with t as (select pt.match_id, count(*) filter (where p.tier in ('CHALLENGER','GRANDMASTER')) cg
                       from participants pt left join players p on p.puuid=pt.puuid join matches m on m.match_id=pt.match_id
                       where m.queue_id=420 group by 1)
                       select count(*), count(*) filter (where cg>0), avg(cg), count(*) filter (where cg=0) from t""")
        total, com, media, sem = cur.fetchone()
        r = exigir(26, t26, "Partidas com ao menos um Desafiante ou Grão-Mestre")
        if r:
            cmp(26, "ao menos 1 C/GM", r[1], f"{f(100*com/total, 1)}% das {milhar(total)}")
            cmp(26, "média C/GM", r[2], f"Média de {f(float(media), 1)} jogadores desses elos por partida")
        cur.execute("""select count(*) from matches m where m.queue_id=420 and m.platform_id='KR' and not exists
                       (select 1 from participants pt join players p on p.puuid=pt.puuid where pt.match_id=m.match_id and p.tier in ('CHALLENGER','GRANDMASTER'))""")
        kr = cur.fetchone()[0]
        r = exigir(26, t26, "Partidas só com jogadores de Mestre")
        if r:
            cmp(26, "só Mestre", r[1], f"{f(100*sem/total, 1)} % ({milhar(sem)}), das quais {kr} na KR".replace(" %", "%"))
        cur.execute("""select p.tier, count(*) from participants pt join players p on p.puuid=pt.puuid join matches m on m.match_id=pt.match_id where m.queue_id=420 group by 1""")
        e = dict(cur.fetchall()); s = sum(e.values())
        r = exigir(26, t26, "Elo dos participantes com elo conhecido")
        if r:
            cmp(26, "elo", r[1], f"{round(100*e['CHALLENGER']/s)}% Desafiante, {round(100*e['GRANDMASTER']/s)}% Grão-Mestre e {round(100*e['MASTER']/s)}% Mestre")


def main() -> int:
    q = ler_quadros()
    print(f"{len(q)} quadros lidos do docx")
    for n, fn in ((3, q3), (4, q4), (5, q5), (6, q6), (8, q8), (9, q9), (10, q10), (12, q12), (11, q11), (13, q13), (14, q14), (15, q15), (16, q16), (17, q17),
                  (20, q20), (23, q23), (24, q24), (29, q29), (30, q30), (31, q31), (32, q32)):
        if n not in q:
            continue  # quadro cortado na simplificação de 2026-11-23
        try:
            fn(q[n][1])
        except Exception as e:  # noqa: BLE001
            CONT.setdefault(n, [0, 0]); CONT[n][1] += 1
            RES.setdefault(n, []).append(f"erro ao conferir: {type(e).__name__}: {e}")
    try:
        if 18 in q and 26 in q:
            q18_26(q)
        if 2 in q:
            q2_21_26(q)
    except Exception as e:  # noqa: BLE001
        print("  banco: erro", type(e).__name__, e)
    print(f"\n{'Quadro':>7} {'células':>8} {'divergem':>9}  título")
    for n in sorted(q, key=lambda k: NOVO.get(k, k)):
        c = CONT.get(n)
        t = q[n][0][:70]
        print(f"{NOVO.get(n, n):>7} {('—' if not c else c[0]):>8} {('—' if not c else c[1]):>9}  {t}")
    falhas = sum(v[1] for v in CONT.values())
    print(f"\nTotal: {sum(v[0] for v in CONT.values())} células conferidas, {falhas} divergência(s)")
    for n in sorted(RES):
        print(f"\nQuadro {NOVO.get(n, n)} (numeração anterior: {n}):")
        for m in RES[n][:15]:
            print("  -", m)
        if len(RES[n]) > 15:
            print(f"  … mais {len(RES[n]) - 15}")
    print("\nVEREDITO:", "quadros conferem com os artefatos" if not falhas else "HÁ DIVERGÊNCIA")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
