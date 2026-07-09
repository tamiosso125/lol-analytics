"""Orientação estratégica gerada por LLM a partir do estado da partida
e, opcionalmente, da composição de times.

Camada 1 do plano "conhecimento geral aplicado à predição" (ver
docs/diario_execucao.md 2026-07-08): o modelo ML já diz QUAL a
probabilidade e QUAL fator pesa mais (SHAP) — isso aqui traduz esses
números em orientação de jogo usando o conhecimento geral de League of
Legends da própria LLM. Mesma convenção de honestidade do "Leitura de
jogo:" do NLQ (src/nlq/nl_to_sql.py): claramente separado do dado
observado, e o prompt força a LLM a dizer explicitamente que não é
verificado pelos dados desta partida — o modelo de ML não vê itens,
posição de jogador nem estado de wave/minion (a API da Riot não grava
nada disso).

Camada 2 (2026-07-08): opcionalmente recebe campeões por posição +
matchups de lane + sinergias — os MESMOS números que o /compose já
calcula a partir do histórico real (não são opinião da LLM). O prompt
distingue explicitamente "dado real" de "conhecimento geral" nessas
seções, pra orientação poder citar campeão específico sem inventar
estatística que não foi fornecida.

Camada 3 — análise de draft (2026-07-08, feedback de uso real): além
da orientação em cima de um ESTADO, `generate_draft_analysis()` lê os
10 campeões ANTES de existir qualquer estado de jogo — win condition,
contra-pick, quem escala melhor. Não precisa de MatchState nem
probabilidade do modelo."""
import os

import anthropic

FEATURE_LABELS = {
    "gold_diff": "diferença de ouro",
    "xp_diff": "diferença de XP",
    "kill_diff": "diferença de abates",
    "tower_diff": "diferença de torres",
    "dragon_diff": "diferença de dragões",
}


def _format_player(label: str, pe: dict | None) -> str:
    """pe = subconjunto de player_effect() (name, games_on_champion,
    raw_win_rate, shrunk_win_rate) — win rate do JOGADOR naquele
    campeão específico, já com shrinkage bayesiano pra amostra pequena
    (não precisa checar tamanho de amostra de novo aqui, o shrunk já
    resolve isso: poucos jogos = fica perto da média do campeão)."""
    if not pe or pe.get("games_on_champion", 0) == 0:
        return ""
    raw = pe.get("raw_win_rate")
    raw_txt = f"{raw * 100:.0f}% bruto em {pe['games_on_champion']} jogos, " if raw is not None else ""
    return (
        f" {label} = {pe['name']}: {raw_txt}"
        f"{pe['shrunk_win_rate'] * 100:.0f}% ajustado (shrinkage) NESTE campeão especificamente"
    )


def _format_lanes(lanes: list[dict]) -> str:
    lines = []
    for l in lanes:
        bit = f"- {l['position']}: {l['blue']} vs {l['red']} — "
        bit += (
            f"{l['blue_lane_win_rate'] * 100:.0f}% de vitória do azul em "
            f"{l['matchup_games']} confrontos diretos reais"
            if l.get("matchup_games", 0) >= 10
            else "poucos confrontos diretos no histórico, estimativa aproximada"
        )
        bit += _format_player("jogador azul", l.get("blue_player"))
        bit += _format_player("jogador vermelho", l.get("red_player"))
        lines.append(bit)
    return (
        "Matchups por lane — DADO REAL do histórico de partidas, não opinião "
        "(quando um jogador específico é listado, o win rate dele NAQUELE "
        "campeão importa tanto quanto o matchup — um jogador muito acima ou "
        "abaixo da média no campeão pode inverter a leitura do matchup "
        "puro):\n" + "\n".join(lines)
    )


def _format_synergies(blue_synergies: list[dict], red_synergies: list[dict]) -> str | None:
    sig_blue = [s for s in blue_synergies if s.get("significant")]
    sig_red = [s for s in red_synergies if s.get("significant")]
    if not sig_blue and not sig_red:
        return None
    lines = (
        "\n".join(
            f"- {s['a']} + {s['b']} (time azul): {s['delta'] * 100:+.1f} pontos "
            "percentuais de sinergia (estatisticamente distinguível de ruído)"
            for s in sig_blue
        )
        + "\n"
        + "\n".join(
            f"- {s['a']} + {s['b']} (time vermelho): {s['delta'] * 100:+.1f} "
            "pontos percentuais de sinergia (estatisticamente distinguível de ruído)"
            for s in sig_red
        )
    ).strip()
    return (
        "Sinergias de dupla com significância estatística — DADO REAL, já "
        f"corrigido por amostra pequena (shrinkage + intervalo de confiança):\n{lines}"
    )


def generate_advice(
    state: dict,
    blue_win_probability: float,
    shap_contributions: dict[str, float],
    blue_champions: dict[str, str] | None = None,
    red_champions: dict[str, str] | None = None,
    lanes: list[dict] | None = None,
    blue_synergies: list[dict] | None = None,
    red_synergies: list[dict] | None = None,
    tactical: dict | None = None,
) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    state_lines = "\n".join(
        f"- {FEATURE_LABELS[f]}: {state[f]:+.0f}" for f in FEATURE_LABELS
    )

    sections = [
        f"Você é um analista estratégico de League of Legends. Um modelo de "
        f"machine learning avalia uma partida aos {state['minute']} minutos "
        f"(valores azul menos vermelho):\n\nEstado:\n{state_lines}\n\n"
        f"Probabilidade de vitória do time azul segundo o modelo: "
        f"{blue_win_probability * 100:.1f}%"
    ]

    if shap_contributions:
        shap_lines = "\n".join(
            f"- {FEATURE_LABELS[f]}: {shap_contributions.get(f, 0.0):+.3f}"
            for f in FEATURE_LABELS
        )
        sections.append(
            "Contribuição de cada fator para essa predição (SHAP — positivo "
            f"empurra a favor do azul, negativo a favor do vermelho):\n{shap_lines}"
        )

    # Camada 2: composição — campeões e, quando fornecidos, matchups/
    # sinergias JÁ CALCULADOS do histórico real (não é a LLM adivinhando)
    if blue_champions or red_champions:
        positions = sorted(set(blue_champions or {}) | set(red_champions or {}))
        comp_lines = "\n".join(
            f"- {pos}: {(blue_champions or {}).get(pos, '?')} (azul) vs "
            f"{(red_champions or {}).get(pos, '?')} (vermelho)"
            for pos in positions
        )
        sections.append(f"Composição de times por posição:\n{comp_lines}")

    if lanes:
        sections.append(_format_lanes(lanes))

    syn_block = _format_synergies(blue_synergies or [], red_synergies or [])
    if syn_block:
        sections.append(syn_block)

    # Camada 2 (itens) + Camada 3 (posições/visão/momentum) — dado REAL
    # da timeline desta partida, no minuto analisado (src/coach/tactics.py)
    has_tactical = bool(
        tactical
        and (tactical.get("items") or tactical.get("spatial") or tactical.get("vision"))
    )
    if tactical and tactical.get("items"):
        item_lines = "\n".join(
            f"- {champ}: {', '.join(its)}" for champ, its in tactical["items"].items()
        )
        sections.append(
            f"Itens finalizados que cada campeão JÁ possuía aos "
            f"{tactical['minute']} minutos — DADO REAL desta partida:\n{item_lines}"
        )
    if tactical and tactical.get("spatial"):
        sp = tactical["spatial"]
        spatial_bits = []
        for team, label in (("blue", "Time azul"), ("red", "Time vermelho")):
            s = sp.get(team)
            if not s:
                continue
            bit = f"{label}: {s['grouping']}"
            if s["overextended"]:
                bit += f", {s['overextended']} jogador(es) avançado(s) na metade inimiga"
                if s["deep_overextended"]:
                    bit += f" ({s['deep_overextended']} bem fundo, arriscado)"
            spatial_bits.append(bit)
        jd = tactical.get("jungle_diff", 0)
        jungle_txt = (
            f"\nTempo de selva (camps neutros farmados, azul − vermelho): {jd:+d}"
            if jd else ""
        )
        sections.append(
            f"Posição aproximada dos times aos {tactical['minute']} minutos "
            f"(1 amostra por minuto — dá pra ler agrupamento e quem está "
            f"avançado, NÃO o estado de wave/minion):\n"
            + "\n".join(spatial_bits) + jungle_txt
        )

    window = tactical.get("window") if tactical else None
    if tactical and tactical.get("vision"):
        v = tactical["vision"]
        vision_txt = (
            f"- Azul: {v['blue']['control']} wards de controle + "
            f"{v['blue']['normal']} wards normais\n"
            f"- Vermelho: {v['red']['control']} wards de controle + "
            f"{v['red']['normal']} wards normais"
        )
        sections.append(
            f"Wards colocadas nos últimos {window} minutos (contagem exata "
            f"de evento, não é aproximação) — DADO REAL desta partida:\n{vision_txt}"
        )
    if tactical and tactical.get("kills_window"):
        kw = tactical["kills_window"]
        if kw["blue"] or kw["red"]:
            sections.append(
                f"Abates nos últimos {window} minutos (momentum recente, "
                f"distinto da diferença acumulada do jogo todo) — DADO REAL "
                f"desta partida:\nAzul {kw['blue']} × {kw['red']} Vermelho"
            )

    instructions = (
        "\n\nCom base nisso, escreva uma orientação estratégica curta (4-8 "
        "frases — mais perto de 8 se houver recomendação de build pra "
        "incluir, 4-6 caso contrário — português do Brasil, texto corrido, "
        "sem markdown) para o time em desvantagem (ou para os dois lados, "
        "se a diferença for pequena) sobre o que costuma ser prioridade "
        "numa situação assim — controle de objetivo, prioridade de rota, "
        "quando lutar ou evitar luta, que tipo de vantagem precisa ser "
        "convertida antes que o adversário se recupere."
    )
    if blue_champions or red_champions:
        instructions += (
            " Cite campeões específicos quando fizer sentido (power spike, "
            "papel na composição, o matchup/sinergia listado acima) em vez de "
            "só falar em 'time azul'/'time vermelho' — mas só cite número de "
            "matchup/sinergia se ele foi listado acima; não invente estatística."
        )
    if has_tactical and (blue_champions or red_champions):
        instructions += (
            " Inclua também uma recomendação de build: olhando os itens que "
            "cada time JÁ tem (listados acima) e o equilíbrio squishy/tanque "
            "da composição inimiga, sugira o próximo item ou uma mudança de "
            "prioridade de build pra quem estiver montado errado pro que "
            "enfrenta (ex.: time inimigo muito squishy pede itens de "
            "penetração/execução em vez de sobrevivência; time inimigo com "
            "muito CC/engajamento pede resistência antes de dano puro). Isso "
            "é leitura de conhecimento geral sobre os campeões, não dado "
            "medido — não invente porcentagem de redução de dano ou número "
            "específico."
        )
    elif blue_champions or red_champions:
        instructions += (
            " Se fizer sentido, comente que tipo de prioridade de build cada "
            "lado deveria ter dado o equilíbrio squishy/tanque das duas "
            "composições — leitura de conhecimento geral, não dado medido "
            "(itens atuais desta partida não estão disponíveis aqui)."
        )
    if has_tactical:
        instructions += (
            " Aproveite os itens, a leitura de posição/agrupamento, visão "
            "(wards) e momentum de abates recente acima na orientação (ex.: "
            "quem já tem item-chave, quem está avançado demais sem visão "
            "própria, qual time está no controle da luta agora) — mas trate "
            "a posição como aproximada (1 amostra/minuto); wards e abates da "
            "janela são contagem exata."
        )
    instructions += (
        " Use conhecimento geral de macro/estratégia de League of Legends "
        "pra tudo que não for dado explícito acima.\n\n"
    )
    if has_tactical:
        instructions += (
            "Termine com uma frase curta deixando claro que itens e posição "
            "são dado real desta partida mas a posição é aproximada (1 amostra "
            "por minuto), e que o estado de wave/minion não é observável — a "
            "leitura tática fina depende disso."
        )
    else:
        instructions += (
            "Termine com uma frase curta deixando claro que isso é leitura "
            "estratégica geral aplicada a este estado — não uma recomendação "
            "verificada pelos dados desta partida específica, já que o modelo "
            "não vê itens, posição dos jogadores nem controle de wave."
        )

    prompt = "\n\n".join(sections) + instructions

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=750,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def generate_draft_analysis(
    blue_champions: dict[str, str],
    red_champions: dict[str, str],
    lanes: list[dict] | None = None,
    blue_synergies: list[dict] | None = None,
    red_synergies: list[dict] | None = None,
) -> str:
    """Leitura de draft — ANTES de existir qualquer estado de jogo
    observável, só os 10 campeões escolhidos. Não usa MatchState nem
    probabilidade do modelo (o modelo de ML não recebe campeão como
    entrada de qualquer forma — isso aqui é uma pergunta diferente:
    "quem tem vantagem estratégica pelo draft", não "quem está ganhando
    agora"). Pedido explícito de feedback de uso real: "fala sobre o
    draft em si — qual a win condition, quem contra-pica quem, o time
    tem resposta pro win condition do outro" (docs/diario_execucao.md
    2026-07-08)."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    positions = sorted(set(blue_champions) | set(red_champions))
    comp_lines = "\n".join(
        f"- {pos}: {blue_champions.get(pos, '?')} (azul) vs "
        f"{red_champions.get(pos, '?')} (vermelho)"
        for pos in positions
    )
    sections = [
        "Você é um analista/caster de League of Legends fazendo uma leitura "
        "de DRAFT — a partida ainda NÃO começou, não há ouro/XP/abates "
        "observados ainda, só os 10 campeões escolhidos:\n\n"
        f"Composição de times por posição:\n{comp_lines}"
    ]

    if lanes:
        sections.append(_format_lanes(lanes))
    syn_block = _format_synergies(blue_synergies or [], red_synergies or [])
    if syn_block:
        sections.append(syn_block)

    has_player = any(l.get("blue_player") or l.get("red_player") for l in (lanes or []))
    instructions = (
        "\n\nEscreva uma leitura de draft no estilo de um analista "
        "comentando antes do jogo começar (8-12 frases, português do "
        "Brasil, texto corrido, sem markdown), cobrindo:\n"
        "- Qual é a win condition de cada time — qual jogador/lane precisa "
        "carregar, baseado no potencial de scaling e no papel dos campeões "
        "escolhidos (força no early vs no late, engajador vs peeler, dano "
        "físico vs mágico);\n"
        "- Onde estão os matchups favoráveis/perdidos — use os dados reais "
        "de matchup listados acima quando disponíveis; senão, conhecimento "
        "geral de contra-pick/scaling entre os campeões envolvidos;\n"
        "- Se o time favorecido tem resposta pra win condition do outro "
        "(ex.: peel, CC em área, itens que respondem ao snowball de um "
        "carry específico) — isso muda a leitura de quem realmente tem "
        "caminho pra vitória;\n"
        "- Seja direto se um lado claramente não tem caminho razoável pra "
        "vitória mesmo convertendo sua melhor win condition, ou se o draft "
        "está equilibrado — não amacie a leitura por educação.\n"
    )
    if has_player:
        instructions += (
            "- Quando um jogador específico tem win rate listado NAQUELE "
            "campeão (acima ou abaixo da média), pondere isso na leitura — "
            "um jogador muito melhor ou pior que a média no campeão pode "
            "compensar (ou piorar) uma desvantagem estrutural de matchup; "
            "diga isso explicitamente quando for o caso, não só analise os "
            "campeões como se fossem jogados na média.\n"
        )
    instructions += (
        "\nDeixe claro o que é dado real (matchup/sinergia/win rate de "
        "jogador listados acima, se houver) vs sua leitura de conhecimento "
        "geral sobre os campeões (kit, scaling, contra-pick, meta) — não "
        "invente número que não foi te dado. Termine com uma frase "
        "resumindo o veredito geral da leitura de draft, deixando claro que "
        "é uma leitura ESTRATÉGICA pré-jogo (quem tem o caminho mais fácil "
        "pro sucesso no papel) — não uma predição do resultado: um draft "
        "pior no papel pode vencer por execução, early game agressivo ou "
        "erro do adversário, então a leitura pode não bater com o "
        "resultado real da partida."
    )

    prompt = "\n\n".join(sections) + instructions

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=900,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
