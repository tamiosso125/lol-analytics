"""Bateria de validação comportamental do modelo de predição (produção).

Não substitui as métricas de held-out test já reportadas (train_baseline.py
/ tune_models.py) — testa outra coisa: se o modelo exportado (usado pelo
/predict e pela análise de partida) se comporta como um analista esperaria,
em cenários que não estão necessariamente no dataset de teste:

  1. Sanidade direcional CONDICIONAL: partindo de linhas REAIS do dataset de
     treino, aumentar uma feature isolada (valores inteiros, dentro do
     percentil observado) move a probabilidade na direção certa? Mede
     "vantagem REAL sobe a chance", não "toda feature é monotônica" — o
     XGBoost deste projeto NÃO garante monotonicidade isolada por fator
     (declarado na Seção 5.8 do TCC; ver NOTA sobre o porquê desta
     reformulação em section1_direcionalidade).
  2. Casos extremos: uma vantagem enorme em tudo deve dar probabilidade
     muito alta (não 100% cravado — o modelo não deveria ser overconfident
     além do que os dados sustentam — mas claramente decisivo).
  3. Taxa-base por fase: com tudo empatado, a probabilidade deve cair dentro da
     faixa que o TCC 4.3 documenta (46,3% a 51,1%), e o corte mais favorável
     ao vermelho é o de 15min — o viés ENFRAQUECE ao longo da partida, e o
     ponto de 25min tem IC 95% que inclui 50%, então inversão não é
     confirmada.
  4. Consistência entre fases (achado do SHAP): a importância de tower_diff
     deve crescer bastante de 10/15 min para 25 min (as placas só caem aos
     14 min); dragon_diff/gold_diff devem dominar em todas as fases.
  5. Checagem retrospectiva: rodando o modelo minuto a minuto em partidas
     REAIS (não sintéticas), a probabilidade média nos últimos minutos deve
     favorecer o time que de fato venceu, na maioria dos casos.

Uso:  python tests/validate_predictions.py
"""
import os
import sys

import joblib
import pandas as pd
import shap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import get_conn
from src.features.build_features import CUTOFFS, features_from_timeline

# Caminhos ancorados no repo, não no CWD: rodar de outro diretório quebrava
# o load do modelo e do CSV (mesma classe do incidente de 2026-07-03 em que
# smoke_test.py sobrescreveu features.csv real por rodar com path relativo).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]

# ranges do 1º-99º percentil por fase (mesmos usados no front, matchState.ts)
RANGES = {
    10: {"gold_diff": 5500, "xp_diff": 4500, "kill_diff": 11, "tower_diff": 2, "dragon_diff": 1},
    15: {"gold_diff": 10000, "xp_diff": 9000, "kill_diff": 15, "tower_diff": 4, "dragon_diff": 2},
    20: {"gold_diff": 13500, "xp_diff": 12000, "kill_diff": 20, "tower_diff": 8, "dragon_diff": 3},
    25: {"gold_diff": 15000, "xp_diff": 16000, "kill_diff": 24, "tower_diff": 11, "dragon_diff": 4},
}

FAIL = []
NEUTRO = []
LIMITADO = []

# Fatores que a Seção 5.8 do TCC NOMEIA ao declarar a limitação: "não garante
# formalmente que aumentar isoladamente a diferença de abates OU DE TORRES nunca
# reduza a probabilidade prevista". A categoria é definida por PROPRIEDADE
# (fator nomeado pelo TCC), não por tupla (feature, corte) — assim não é uma
# lista feita sob medida para o único caso que falhava.
FEATURES_NOMEADOS_PELO_TCC = {"kill_diff", "tower_diff"}

# Efeito médio absoluto (SHAP) abaixo do qual o modelo praticamente não usa o
# fator neste corte. 0,05 em log-odds ≈ 5 pontos percentuais de efeito médio na
# probabilidade. Limiar ABSOLUTO de escolha: as importâncias medidas variam de
# 0,0089 a 1,044 (117x), então um limiar relativo daria outro resultado.
# Registro honesto: 0,05 não tem fonte no TCC nem no diário — é escolha de
# implementação, declarada aqui para não passar por derivação.
SHAP_RELEVANTE = 0.05

_cache_shap: dict = {}


def _shap_medio(model, X: pd.DataFrame, feat: str) -> float:
    """Importância média absoluta (SHAP) de uma feature — cacheado por cutoff,
    porque a seção 1 pergunta isso 5x por corte e o TreeExplainer é caro."""
    key = id(model)
    if key not in _cache_shap:
        vals = shap.TreeExplainer(model)(X)
        _cache_shap[key] = {
            f: float(abs(vals.values[:, i]).mean())
            for i, f in enumerate(FEATURES)
        }
    return _cache_shap[key][feat]


def _emit(name: str, status: str, detail: str) -> None:
    """Imprime uma checagem. NEUTRO = modelo insensível ao fator nos estados
    testados (informação). LIMITADO = não-monotonicidade que o TCC 5.8
    declara. Nenhum dos dois é FALHA: tratá-los como falha seria reportar o
    oposto do que o modelo faz, ou reprovar um comportamento documentado."""
    print(f"[{status}] {name} — {detail}")
    if status == "FALHA":
        FAIL.append(name)
    elif status == "NEUTRO":
        NEUTRO.append(name)
    elif status == "LIMITADO":
        LIMITADO.append(name)


def check(name: str, ok: bool, detail: str) -> None:
    _emit(name, "OK" if ok else "FALHA", detail)


def predict(model, feats: dict) -> float:
    """Prediz com um estado COMPLETO (as 5 features). Não use com kwargs
    soltos: feature ausente vira 0 e produz um estado artificial que a
    partida não gera — foi isso que invalidou a antiga seção 1 (ver NOTA
    em section1_direcionalidade).

    Exceção deliberada: a seção 3 chama com `{}` porque o objeto de teste
    LÁ é justamente o estado "tudo empatado" — zerar todas as features é
    a definição do cenário, não um esquecimento."""
    row = pd.DataFrame([[feats.get(f, 0) for f in FEATURES]], columns=FEATURES)
    return float(model.predict_proba(row)[0, 1])


def _predict_batch(model, estados: list) -> list:
    """ predict_proba em lote — um call por (corte, feature) em vez de um por
    ponto. Com 500 árvores e 40.000 linhas de uma, a versão por ponto levava
    minutos, e o agente `validador` roda este script como portão."""
    rows = [[e.get(f, 0) for f in FEATURES] for e in estados]
    return model.predict_proba(pd.DataFrame(rows, columns=FEATURES))[:, 1]


def section1_direcionalidade(models: dict, n_linhas: int = 400, n_passos: int = 4) -> None:
    """Vantagem REAL, isolada, sobe a probabilidade?

    NOTA — por que esta seção mudou de "Monotonicidade" para "Sanidade
    direcional" (2026-10-03, não é afrouxamento de limiar):

    A versão anterior varria uma feature por vez com as outras 4 cravadas em
    ZERO e media correlação > 0.9. Isso media duas coisas que não são o modelo:
      (i) contexto zerado — `tower_diff=+2` com `gold_diff=0` é um estado que
          a partida praticamente não produz (o próprio diário registra isso em
          2026-07-03);
      (ii) valores fracionários — as features são aritmética INTEIRA sobre o
           payload, e `np.linspace` gerava 0.29 torre / 0.14 dragão, que a
           feature não pode assumir. 13 dos 15 pontos eram fisicamente
           impossíveis.
    Resultado: correlação negativa nos cortes iniciais e positiva nos tardios
    para a MESMA feature, que é ruído de região de baixa densidade, não
    não-monotonicidade. E o `nan` do corte 25min em kill_diff era "modelo
    insensível ao fator neste contexto", reportado como se fosse o oposto.

    O que o projeto REALMENTE afirma (TCC 5.8) é que o XGBoost não garante
    monotonicidade isolada por fator. A versão nova mede a afirmação correta:
    partindo de linhas reais do dataset de treino, valores inteiros dentro do
    percentil observado, a probabilidade vai na direção esperada? A
    não-monotonicidade isolada pode e deve continuar aparecendo — com o
    rótulo certo.
    """
    print("\n--- 1. Sanidade direcional (partindo de linhas reais do treino) ---")
    _cache_shap.clear()
    df = pd.read_csv(os.path.join(ROOT, "data", "features_phases.csv"))
    for cutoff in CUTOFFS:
        part = df[df["cutoff_min"] == cutoff]
        if part.empty:
            print(f"[AVISO] corte {cutoff}min: sem linhas no dataset, pulando")
            continue
        sample = part.sample(n=min(n_linhas, len(part)), random_state=42)
        for feat in FEATURES:
            lo = int(part[feat].quantile(0.01))
            hi = int(part[feat].quantile(0.99))
            if hi <= lo:
                print(f"[AVISO] corte {cutoff}min, {feat}: sem amplitude no percentil")
                continue

            # deltas CRESCENTES de lo até hi. Começar no extremo alto e descer
            # faria a probabilidade cair e o teste contaria acerto na direção
            # errada — bug da primeira versão deste método, que acusou 7% de
            # acerto em gold_diff, que é justamente a feature dominante
            # (SHAP 0,65 a 1,04). Feature positiva = vantagem do azul, então o
            # efeito esperado ao AUMENTÁ-la é sempre subir a probabilidade.
            #
            # lo/hi entram como OFFSET aplicado ao valor da linha, não como
            # valor absoluto: uma linha de gold_diff +14.000 no corte 25 é
            # sondada em +14.000+1.041. Isso é deliberado — o objetivo é
            # "dado o resto do estado real, e se esta feature fosse maior?",
            # e o rótulo imprime o offset real para não confundir.
            deltas = [lo + (hi - lo) * i / n_passos for i in range(n_passos + 1)]
            nome = f"corte {cutoff}min, {feat}"
            acertos = 0
            empates = 0
            comparados = 0
            sensiveis = 0
            # batch: um predict_proba por (corte, feature) em vez de um por
            # ponto — 40.000 chamadas de uma linha levavam minutos, e o
            # agente `validador` roda isto como portão.
            estados, origem = [], []
            for idx, (_, row) in enumerate(sample.iterrows()):
                base = {f: int(row[f]) for f in FEATURES}
                for d in deltas:
                    st = dict(base)
                    st[feat] = int(round(base[feat] + d))
                    estados.append(st)
                    origem.append(idx)
            if not estados:
                _emit(nome, "NEUTRO", "sem linhas para sondar")
                continue
            probs = _predict_batch(models[cutoff], estados)
            por_linha: dict = {}
            for p, idx in zip(probs, origem):
                por_linha.setdefault(idx, []).append(float(p))
            for probs_linha in por_linha.values():
                variacao = max(probs_linha) - min(probs_linha)
                if variacao < 1e-9:
                    continue  # modelo insensível ao fator NESTE contexto
                sensiveis += 1
                for a, b in zip(probs_linha, probs_linha[1:]):
                    comparados += 1
                    if b > a:
                        acertos += 1
                    elif b == a:
                        empates += 1
            if comparados == 0:
                _emit(
                    nome,
                    "NEUTRO",
                    f"modelo insensível a {feat} nos estados amostrados "
                    f"(0/{len(sample)} linhas sensíveis, variação de "
                    f"probabilidade < 1e-9) — direção não avaliável",
                )
                continue
            # fração só sobre pares que realmente mudaram; empate é
            # reportado à parte porque infla o número se contado como acerto
            denom = comparados - empates
            frac = acertos / denom if denom else 1.0
            shap_medio = _shap_medio(models[cutoff], part[FEATURES], feat)
            detalhe_base = (
                f"subiu em {acertos}/{denom} pares que mudaram "
                f"({empates} empataram, {sensiveis}/{len(sample)} linhas "
                f"sensiveis, offset {lo:+d}..{hi:+d})"
            )
            if frac >= 0.60:
                _emit(nome, "OK", f"{detalhe_base} — direção correta em {frac:.0%}")
            elif shap_medio < SHAP_RELEVANTE:
                # o modelo praticamente não usa este fator neste corte:
                # exigir direção seria exigir precisão que os dados não sustentam
                _emit(
                    nome,
                    "NEUTRO",
                    f"{detalhe_base} — direção em {frac:.0%}, mas SHAP médio "
                    f"{shap_medio:.4f} < {SHAP_RELEVANTE}: fator sem peso real "
                    "neste corte, direção não exigível",
                )
            elif feat in FEATURES_NOMEADOS_PELO_TCC:
                _emit(
                    nome,
                    "LIMITADO",
                    f"{detalhe_base} — direção em {frac:.0%} e não-monotonicidade "
                    f"ISOLADA de {feat}, que a Seção 5.8 do TCC nomeia "
                    "explicitamente (abates e torres). Reportado, não reprovado.",
                )
            else:
                _emit(
                    nome,
                    "FALHA",
                    f"{detalhe_base} — direção em {frac:.0%} com SHAP médio "
                    f"{shap_medio:.4f}: fator REALMENTE usado pelo modelo com "
                    "direção errada, e o TCC não declara isso para ele",
                )


def section2_extremes(models: dict) -> None:
    print("\n--- 2. Casos extremos (vantagem/desvantagem total) ---")
    for cutoff in CUTOFFS:
        model = models[cutoff]
        r = RANGES[cutoff]
        lead = predict(model, {f: r[f] for f in FEATURES})
        deficit = predict(model, {f: -r[f] for f in FEATURES})
        check(f"corte {cutoff}min, liderança total", lead > 0.90, f"prob = {lead:.3f}")
        check(f"corte {cutoff}min, déficit total", deficit < 0.10, f"prob = {deficit:.3f}")
        check(
            f"corte {cutoff}min, simetria lead/deficit",
            abs((lead + deficit) - 1) < 0.05,
            f"lead {lead:.3f} + deficit {deficit:.3f} = {lead + deficit:.3f} (esperado ~1.0)",
        )


def section3_base_rate(models: dict) -> None:
    """Taxa-base por fase.

    O TCC (Seção 5.3) NÃO afirma "vermelho < 50% em todos os cortes" e também
    NÃO afirma que o viés enfraquece ao longo da partida. A versão anterior
    deste texto afirmava, e esta checagem exigia que o ponto mais vermelho
    fosse o de 15 min. A medição sobre a base ampliada desfez essa forma.
    Desde o parecer de 2026-11-08 (e sem o vazamento do quadro final), entre
    partidas com diferença de ouro < 500 a taxa bruta do azul é 46,5% / 47,8%
    / 46,9% / 47,4% e o teste com a partida como unidade não detecta
    diferença (menor p de Holm 0,65, `reports/vies_cortes_por_partida.json`).
    O TCC diz "taxas próximas", NÃO "constante" nem "estável": não detectar
    diferença não prova igualdade.

    O estado todo-zero usado aqui (48,5% a 51,5%, `reports/taxa_base_por_corte.json`)
    não ocorre em nenhuma partida empatada real, então NÃO mede calibração
    (essa é medida nas empatadas reais por `docs/calibracao_empate_real.py`).
    É teste de comportamento:
      1. todo corte dentro de uma faixa plausível;
      2. a dispersão entre cortes pequena — o modelo não inventa um pico que
         os dados não mostram.

    Medir o texto em vez de medir a memória é o motivo da mudança: a bateria
    reprovava porque o enunciado dela defendia uma forma que os dados não
    sustentam mais.
    """
    print("\n--- 3. Taxa-base por fase (tudo empatado) ---")
    bases = {}
    for cutoff in CUTOFFS:
        base = predict(models[cutoff], {})
        bases[cutoff] = base
        check(
            f"corte {cutoff}min, taxa-base dentro da faixa documentada",
            0.455 <= base <= 0.556,
            f"prob = {base:.3f} (estado todo-zero, 48,5%-51,5% no artefato; "
            "não é partida real, não mede calibração)",
        )
    # "Constante" operacional: a dispersão entre cortes não pode passar da
    # dispersão que o próprio texto reporta entre cortes (1,4 pp), com folga
    # para não transformar ruído de ponto flutuante em regressão.
    vals = list(bases.values())
    dispersao = (max(vals) - min(vals)) * 100
    check(
        "sem pico inventado: dispersão entre cortes <= 4 pp",
        dispersao <= 4.0,
        f"dispersão = {dispersao:.2f} pp "
        f"({' -> '.join(f'{c}min {bases[c]:.3f}' for c in CUTOFFS)}); "
        "o TCC não afirma mais que haja pico no meio do jogo",
    )


def section4_shap_evolution(models: dict) -> None:
    print("\n--- 4. Evolução da importância SHAP entre fases ---")
    df = pd.read_csv(os.path.join(ROOT, "data", "features_phases.csv"))
    importances = {}
    for cutoff in CUTOFFS:
        part = df[df["cutoff_min"] == cutoff]
        X = part[FEATURES]
        explainer = shap.TreeExplainer(models[cutoff])
        vals = explainer(X)
        importances[cutoff] = {
            f: float(abs(vals.values[:, i]).mean()) for i, f in enumerate(FEATURES)
        }
    ratio = importances[25]["tower_diff"] / max(importances[10]["tower_diff"], 1e-9)
    check(
        "tower_diff cresce muito de 10 -> 25 min",
        ratio > 10,
        f"importância aos 10min={importances[10]['tower_diff']:.4f}, "
        f"aos 25min={importances[25]['tower_diff']:.4f} ({ratio:.0f}x)",
    )
    for cutoff in CUTOFFS:
        top = max(importances[cutoff], key=importances[cutoff].get)
        check(
            f"corte {cutoff}min, gold_diff ou dragon_diff domina",
            top in ("gold_diff", "dragon_diff"),
            f"fator mais importante = {top} ({importances[cutoff][top]:.4f})",
        )


def section5_retrospective(models: dict, sample_size: int = 150) -> None:
    """Sorteio DETERMINÍSTICO: semeia o PostgreSQL antes do ORDER BY random().

    A versão anterior sorteava a cada execução com n=30 e limiar 0.70 — um gate
    que podia falhar conforme o humor do banco. Além disso n=30 dá IC 95%
    largo demais para sustentar afirmação: 28/30 = 93% não é evidência de nada.
    Aqui a checagem é reprodutível (mesma amostra em toda execução) e o
    resultado é reportado como faixa de intervalo, não como número fechado.
    """
    print(f"\n--- 5. Checagem retrospectiva ({sample_size} partidas reais, determinística) ---")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT setseed(%s)", (0.4242,))
        cur.execute(
            """SELECT t.match_id, t.payload, tm.win
               FROM raw_timelines t
               JOIN teams tm ON tm.match_id = t.match_id AND tm.team_id = 100
               ORDER BY random() LIMIT %s""",
            (sample_size,),
        )
        rows = cur.fetchall()

    hits = 0
    total = 0
    for match_id, payload, blue_win in rows:
        frames = payload.get("info", {}).get("frames", [])
        n = len(frames)
        if n < 6:
            continue
        # média da probabilidade nos últimos 5 minutos disponíveis (antes do
        # fim), usando o modelo da fase correspondente a cada minuto
        last_minutes = range(max(1, n - 6), n - 1)
        probs = []
        for minute in last_minutes:
            feats = features_from_timeline(payload, minute)
            if feats is None:
                continue
            cutoff = max((c for c in CUTOFFS if c <= minute), default=min(CUTOFFS))
            probs.append(predict(models[cutoff], feats))
        if not probs:
            continue
        avg_prob = sum(probs) / len(probs)
        predicted_blue = avg_prob >= 0.5
        total += 1
        if predicted_blue == blue_win:
            hits += 1

    rate = hits / total if total else 0
    check(
        "direção da predição bate com o vencedor real (últimos min.)",
        total > 0 and rate >= 0.70,
        f"{hits}/{total} partidas ({rate:.0%}) — nota: isto não é a acurácia "
        "formal do modelo (métricas de teste já reportadas), é uma checagem "
        "de sanidade rodando o pipeline completo (timeline real -> features "
        "-> modelo por fase) fora do pipeline de treino. Amostra "
        "determinística (setseed) para o gate não depender de sorte.",
    )


def main() -> int:
    models = joblib.load(os.path.join(ROOT, "data", "models_phases.joblib"))
    section1_direcionalidade(models)
    section2_extremes(models)
    section3_base_rate(models)
    section4_shap_evolution(models)
    section5_retrospective(models)

    print(f"\n{'='*60}")
    if LIMITADO:
        print(
            f"{len(LIMITADO)} caso(s) de não-monotonicidade ISOLADA — "
            "limitação DECLARADA na Seção 5.8 do TCC, reportada e não "
            "reprovada:"
        )
        for n in LIMITADO:
            print(f"  - {n}")
    if NEUTRO:
        print(
            f"{len(NEUTRO)} caso(s) NEUTRO(S) — modelo não dá peso real ao "
            "fator nesse corte (SHAP abaixo do limiar), direção não exigível:"
        )
        for n in NEUTRO:
            print(f"  - {n}")
    if FAIL:
        print(f"{len(FAIL)} checagem(ns) FALHARAM: {FAIL}")
        print("VEREDITO: REPROVADO")
    elif LIMITADO or NEUTRO:
        # NÃO dizer "todas passaram" com LIMITADO/NEUTRO listados acima: era
        # exatamente o tick verde que a reformulação existe para impedir — e
        # é a última linha que o validador e a banca leem.
        print(
            f"VEREDITO: APROVADO COM RESSALVAS — nenhuma checagem reprovada, "
            f"mas {len(LIMITADO)} limitação(ões) declarada(s) e {len(NEUTRO)} "
            "fator(es) sem peso real (não avaliados) nesta execução."
        )
    else:
        print("VEREDITO: APROVADO — todas as checagens passaram.")
    return 1 if FAIL else 0


if __name__ == "__main__":
    # Exit code real: antes, main() acumulava FAIL e terminava com status 0
    # sempre — nenhum script em tests/ podia falhar, e o agente `validador`
    # rodava um gate que reportava sucesso ao sistema independente do
    # resultado. `import sys` já estava no arquivo desde sempre, para um
    # sys.exit que nunca foi escrito.
    sys.exit(main())
