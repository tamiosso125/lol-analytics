"""Reescreve em docs/tcc2_texto.md os quadros numéricos a partir de reports/*.json.

Por que existe (2026-11-06): ao refazer o pipeline sobre as 41.063 partidas, ~300 células de
quadros mudaram. Digitar à mão é o erro que o AGENTS.md proíbe; aqui a célula nasce do artefato,
com o mesmo formato que `verifica_tcc.py` exige. Só mexe nas linhas de dados de cada quadro; o
texto corrido continua à mão e é conferido por `verifica_tcc.py`.
Uso: python docs/regenera_quadros.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
MD = RAIZ / "docs" / "tcc2_texto.md"
t = MD.read_text(encoding="utf-8")


def J(nome):
    return json.loads((RAIZ / "reports" / nome).read_text(encoding="utf-8"))


def f(x, d=4, sinal=False):
    s = f"{x:+.{d}f}" if sinal else f"{x:.{d}f}"
    return s.replace("-", "−").replace(".", ",")


def n(x):
    return f"{x:,}".replace(",", ".")


def ic(m, lo, hi):
    return f"{f(m, 4, True)} ({f(lo, 4, True)} a {f(hi, 4, True)})"


def linhas_de(titulo, ate=None):
    """(início, fim, linhas) das linhas de dados do quadro que começa em `titulo`."""
    i = t.index(titulo)
    k = t.index("|---", i)
    k = t.index("\n", k) + 1
    fim = t.find("\n\n", k)
    return k, fim, t[k:fim].split("\n")


def troca(titulo, novas):
    global t
    k, fim, _ = linhas_de(titulo)
    t = t[:k] + "\n".join(novas) + t[fim:]


def cel(l):
    return [x.strip() for x in l.strip().strip("|").split("|")]


# ---- Apêndice C: métricas por corte (metricas_corte.json) ------------------------------------
mc = J("metricas_corte.json")["resultados"]
rot = {"*Random Forest*": "RandomForest", "**XGBoost**": "XGBoost", "MLP": "MLP"}
_, _, ls = linhas_de("Quadro — Métricas completas por corte temporal")
novas = []
for l in ls:
    c = cel(l)
    corte = c[0].split()[0]
    r = mc[corte][rot[c[3]]]
    novas.append(f"| {corte} min | {n(r['n'])} | {f(r['taxa_vitoria_azul'], 3)} | {c[3]} | {f(r['acuracia'])} | "
                 f"{f(r['precisao'])} | {f(r['recall'])} | {f(r['f1'])} | {f(r['auc'])} |")
troca("Quadro — Métricas completas por corte temporal", novas)

# ---- Quadro 3 (corpo): comparação após o ajuste (2026-11-08, parecer do orientador) -------
aj = J("metricas_ajustados.json")["modelos"]
an = J("tune_models_aninhado.json")["modelos"]


def linha_q3(nome, r, aninhado="—"):
    return (f"| {nome} | {f(r['acuracia'])} | {f(r['precisao'])} | {f(r['recall'])} | {f(r['f1'])} | "
            f"{f(r['auc'])} | {aninhado} |")


troca("Quadro — Comparação entre modelos após o ajuste (corte de 15 minutos)", [
    linha_q3("Regressão logística (sem hiperparâmetro ajustado)", aj["Regressão logística"]),
    linha_q3("MLP ajustado", aj["MLP ajustado"], f(an["MLP"]["auc"])),
    linha_q3("XGBoost ajustado (produção)", mc["15"]["XGBoost"], f(an["XGBoost"]["auc"])),
    linha_q3("*Random Forest* ajustada", aj["Random Forest ajustada"], f(an["RandomForest"]["auc"])),
    linha_q3("MLP (referência)", mc["15"]["MLP"]),
    linha_q3("*Random Forest* (referência)", mc["15"]["RandomForest"]),
])

_, _, ls = linhas_de("Quadro — Desempenho do XGBoost por corte temporal")
novas = []
for l in ls:
    corte = cel(l)[0].split()[0]
    r = mc[corte]["XGBoost"]
    novas.append(f"| {corte} min | {n(r['n'])} | {f(r['acuracia'])} | {f(r['auc'])} |")
troca("Quadro — Desempenho do XGBoost por corte temporal", novas)

# ---- Apêndice C: regressão logística e diferenças --------------------------------------------
bd = J("baseline_e_diferencas.json")["resultados"]
dif = "XGBoost - Regressão logística"
_, _, ls = linhas_de("Quadro — Regressão logística como baseline")
novas = []
for l in ls:
    c = cel(l)
    corte = c[0].split()[0]
    m = c[1]
    if m == "Regressão logística":
        mod, d = bd[corte]["modelos"][m], bd[corte]["diferencas"][dif]["auc"]
    elif m == "MLP (referência)":
        mod, d = bd[corte]["modelos"]["MLP"], bd[corte]["diferencas"]["XGBoost - MLP"]["auc"]
    else:
        mod, d = bd[corte]["modelos"]["Random Forest"], bd[corte]["diferencas"]["XGBoost - Random Forest"]["auc"]
    novas.append(f"| {corte} min | {m} | {f(mod['acuracia'])} | {f(mod['auc'])} | {ic(*d)} |")
troca("Quadro — Regressão logística como baseline", novas)

# ---- Apêndice C: 5 e 10 dobras ---------------------------------------------------------------
rd = J("robustez_dobras.json")["resultados"]
rotm = {"XGBoost": "XGBoost", "*Random Forest* (referência)": "RandomForest", "MLP (referência)": "MLP"}
_, _, ls = linhas_de("Quadro — Validação cruzada com 5 e com 10 dobras")
novas = []
for l in ls:
    c = cel(l)
    corte = c[0].split()[0]
    r = rd[corte][rotm[c[1]]]
    novas.append(f"| {corte} min | {c[1]} | {f(r['5']['acuracia'])} | {f(r['10']['acuracia'])} | "
             f"{f(r['5']['auc'])} | {f(r['10']['auc'])} |")
troca("Quadro — Validação cruzada com 5 e com 10 dobras", novas)

# ---- Apêndice C: treino no passado -----------------------------------------------------------
ho = J("holdout_temporal.json")["cortes"]
rotd = {"Cronológica 80/20": "cronologica", "Por *patch*": "por_patch", "Aleatória 80/20": "aleatoria"}
_, _, ls = linhas_de("Quadro — Treino no passado e teste no futuro, XGBoost")
novas = []
for l in ls:
    c = cel(l)
    corte = c[0].split()[0]
    r = ho[corte][rotd[c[1]]]["XGBoost"]
    novas.append(f"| {corte} min | {c[1]} | {n(r['n_treino'])} | {n(r['n_teste'])} | {f(r['acuracia'])} | "
                 f"{f(r['auc'])} | {f(r['auc_ic95'][0])} a {f(r['auc_ic95'][1])} |")
troca("Quadro — Treino no passado e teste no futuro, XGBoost", novas)

# ---- Apêndice K -------------------------------------------------------------------------------
exp, hist, hold, ant = J("experimentos_precisao.json"), J("experimento_historico.json"), J("holdout_precisao.json"), J("experimentos_antigos.json")
mapa = [("E12_trajetoria", "xgb_prod"), ("E13_funcao", "xgb_prod"), ("E14_objetivos", "xgb_prod"), ("E15_rico", "xgb_prod"),
        ("E16_campeoes", "xgb_prod"), ("E17_jogadores", "xgb_prod"), ("E18_tudo", "xgb_prod"), ("E18_tudo", "logit")]
_, _, ls = linhas_de("Quadro — Experimentos 12 a 19")
novas = []
for l, (conj, mdl) in zip(ls[:8], mapa):
    c = cel(l)
    a15, a25 = (exp[k][conj][mdl] for k in ("15", "25"))
    novas.append(f"| {c[0]} | {c[1]} | {ic(a15['delta_auc'], a15['ic_lo'], a15['ic_hi'])} | {ic(a25['delta_auc'], a25['ic_lo'], a25['ic_hi'])} |")
gl = J("ganho_variaveis_logit.json")["cortes"]
c = cel(ls[8])
g15, g25 = (gl[k]["logit"]["E18_tudo"] for k in ("15", "25"))
novas.append(f"| {c[0]} | {c[1]} | {ic(g15['ganho_auc'], g15['ic_lo'], g15['ic_hi'])} | "
             f"{ic(g25['ganho_auc'], g25['ic_lo'], g25['ic_hi'])} |")
c = cel(ls[9])
h15, h25 = (hist[k]["5+"]["logit"]["dauc_ic"] for k in ("15", "25"))
novas.append(f"| {c[0]} | {c[1]} | {ic(*h15)} | {ic(*h25)} |")
troca("Quadro — Experimentos 12 a 19", novas)


def d_(corte, chave):
    if chave == "tuning":
        return ant[corte]["tuning_aninhado"]
    if chave in ("sigmoide", "isotonica"):
        return ant[corte]["calibracao"][chave]
    return ant[corte][chave]["xgb_prod"]


chaves = ["A01_barao_arauto", "A02_dispersao", "tuning", "sigmoide", "isotonica", "A05_ouro_itens", "A06_ofensivas",
          "A06_defensivas", "A08_visao_ambas", "A09_dragoes_tipo", "A10_placas"]
_, _, ls = linhas_de("Quadro — Experimentos 1 a 10")
novas = []
for l, ch in zip(ls[:11], chaves):
    c = cel(l)
    a15, a25 = d_("15", ch), d_("25", ch)
    novas.append(f"| {c[0]} | {c[1]} | {ic(a15['delta_auc'], a15['ic_lo'], a15['ic_hi'])} | {ic(a25['delta_auc'], a25['ic_lo'], a25['ic_hi'])} |")
troca("Quadro — Experimentos 1 a 10", novas)

q5 = ["A01_barao_arauto", "A02_dispersao", "tuning", "sigmoide", "A05_ouro_itens", "A06_ofensivas", "A05_ouro_itens",
      "A08_visao_ambas", "A09_dragoes_tipo", "A10_placas"]
_, _, ls = linhas_de("Quadro — Experimentos negativos de enriquecimento")
novas = []
for l, ch in zip(ls[:10], q5):
    c = cel(l)
    novas.append(f"| {c[0]} | {c[1]} | {f(d_('15', ch)['delta_auc'], 4, True)} e {f(d_('25', ch)['delta_auc'], 4, True)} |")
troca("Quadro — Experimentos negativos de enriquecimento", novas)

_, _, ls = linhas_de("Quadro — Variáveis novas em treino no passado")
novas = []
for l in ls:
    c = cel(l)
    corte = c[0].split()[0]
    d = hold["cortes"][corte][rotd[c[1]]]
    novas.append(f"| {c[0]} | {c[1]} | {f(d['base']['xgb_prod']['auc'])} | {f(d['E18_tudo']['logit']['auc'])} | "
                 f"{ic(*d['E18_tudo']['logit']['dauc_vs_base_xgb'])} |")
troca("Quadro — Variáveis novas em treino no passado", novas)

MD.write_text(t, encoding="utf-8", newline="")
print("quadros regenerados")

# ---- Apêndice J (SHAP) e Apêndice F (taxa-base no empate) -- apêndice acrescentado em 2026-11-06 ----
t = MD.read_text(encoding="utf-8")
sh = J("shap_importance_phases.json")
rotv = {"Diferença de ouro": "gold_diff", "Diferença de experiência": "xp_diff", "Diferença de abates": "kill_diff",
        "Diferença de torres": "tower_diff", "Diferença de dragões": "dragon_diff"}
_, _, ls = linhas_de("Quadro — Importância média das variáveis")
novas = []
for l in ls:
    c = cel(l)
    novas.append(f"| {c[0]} | " + " | ".join(f(sh[k][rotv[c[0]]]) for k in ("10", "15", "20", "25")) + " |")
troca("Quadro — Importância média das variáveis", novas)

# ---- quadros do parecer (2026-11-08): 12, 16, 17, 23 e 24 --------------------------------------
tf = J("tune_models_39k.json")
xg = tf["XGBoost"]
rf_p, mlp_p = tf["RandomForest"]["melhor_combinacao"], tf["MLP"]["melhor_combinacao"]
prod = xg["producao"]
n_prod = sum(1 for e in an["XGBoost"]["escolhas_por_dobra"] if all(e.get(k) == v for k, v in prod.items()))
ordinal = f"{xg['posicao_producao_na_grade']}º"
camadas_l = mlp_p["mlpclassifier__hidden_layer_sizes"]
camadas = " e ".join(str(x) for x in camadas_l)
alpha = f"{mlp_p['mlpclassifier__alpha']:g}".replace(".", ",")
troca("Quadro — Configuração dos três modelos comparados", [
    "| XGBoost | 500 árvores, taxa de aprendizado 0,01, profundidade 3 | busca em grade (27 combinações) sobre a base "
    f"de 10.295 partidas, contidas nas {n(xg['linhas'])} da avaliação; repetida nas {n(xg['linhas'])}, "
    + ("a busca escolheu a mesma configuração (1º lugar entre 27) |" if xg["posicao_producao_na_grade"] == 1 else
       f"a produção ficou em {ordinal} lugar, a {f(xg['delta_auc'])} de AUC-ROC da melhor |"),
    "| XGBoost aninhado | grade de 27 combinações escolhida só no treino de cada dobra (3 dobras internas) | "
    f"a produção foi escolhida em {n_prod} das 5 dobras; acurácia {f(an['XGBoost']['acuracia'])}, "
    f"AUC-ROC {f(an['XGBoost']['auc'])} |",
    "| *Random Forest* (referência) | 500 árvores, demais parâmetros do scikit-learn | sem busca em grade |",
    f"| *Random Forest* ajustada | {rf_p['n_estimators']} árvores, profundidade {rf_p['max_depth']}, mínimo de "
    f"{rf_p['min_samples_leaf']} amostras por folha | busca em grade (27 combinações) nas {n(xg['linhas'])}, "
    f"avaliada nas mesmas dobras: {f(aj['Random Forest ajustada']['acuracia'])} e "
    f"{f(aj['Random Forest ajustada']['auc'])}; aninhada: {f(an['RandomForest']['acuracia'])} e "
    f"{f(an['RandomForest']['auc'])} |",
    "| MLP (referência) | camadas de 64 e 32 neurônios, variáveis padronizadas, até 500 iterações | sem busca em grade |",
    f"| MLP ajustado | {'camada' if len(camadas_l) == 1 else 'camadas'} de {camadas} neurônios, regularização "
    f"{alpha}, até 1.000 iterações | busca em grade (9 combinações) nas {n(xg['linhas'])}, avaliada nas mesmas "
    f"dobras: {f(aj['MLP ajustado']['acuracia'])} e {f(aj['MLP ajustado']['auc'])}; aninhada: "
    f"{f(an['MLP']['acuracia'])} e {f(an['MLP']['auc'])} |",
])

ca = J("curva_aprendizado.json")
novas = []
for p_ in ca["curva_15min"]["pontos"]:
    dp = "—" if p_["sorteios"] == 1 else f(p_["auc_dp"])
    novas.append(f"| {n(p_['treino'])} | {f(p_['auc_media'])} | {dp} |")
troca("Quadro — Curva de aprendizado do XGBoost com teste fixo", novas)
troca("Quadro — AUC-ROC do XGBoost por corte, nas partidas elegíveis", [
    f"| {c_} min | {n(r['elegiveis_n'])} | {f(r['elegiveis_auc'])} | {n(r['mesmas_n'])} | {f(r['mesmas_auc'])} |"
    for c_, r in ca["cortes"].items()])

cal = J("calibracao_empate_real.json")


def pct_(x):
    return f(100 * x, 1) + "%"


def pp_(x):
    v = f(x, 2, True)
    return "0,00 pp" if v in ("+0,00", "−0,00") else v + " pp"


troca("Quadro — Calibração do XGBoost nas partidas empatadas", [
    f"| {c_} min | {n(r['empatadas'])} | {pct_(r['taxa_observada'])} ({pct_(r['ic95_observada'][0])} a "
    f"{pct_(r['ic95_observada'][1])}) | {pct_(r['media_prevista_empatadas'])} | {pp_(r['diferenca_pp'])} | "
    f"{f(r['decis_maior_desvio_pp'], 2)} pp |"
    for c_, r in cal["producao_por_corte"].items()])
rotv2 = {"producao": "Produção", "sigmoide": "Sigmoidal", "isotonica": "Isotônica"}
novas = []
for c_ in ("15", "25"):
    for k, nome in rotv2.items():
        r = cal["variantes"][c_][k]
        novas.append(f"| {c_} min | {nome} | {pp_(r['diferenca_pp'])} | {f(r['decis_maior_desvio_pp'], 2)} pp | "
                     f"{f(r['decis_desvio_medio_pp'], 2)} pp | {f(r['brier'])} | {f(r['auc'])} |")
troca("Quadro — Calibração adicional sobre o XGBoost", novas)
MD.write_text(t, encoding="utf-8", newline="")
print("quadros do parecer regenerados")
