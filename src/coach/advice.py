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
estatística que não foi fornecida."""
import os

import anthropic

FEATURE_LABELS = {
    "gold_diff": "diferença de ouro",
    "xp_diff": "diferença de XP",
    "kill_diff": "diferença de abates",
    "tower_diff": "diferença de torres",
    "dragon_diff": "diferença de dragões",
}


def generate_advice(
    state: dict,
    blue_win_probability: float,
    shap_contributions: dict[str, float],
    blue_champions: dict[str, str] | None = None,
    red_champions: dict[str, str] | None = None,
    lanes: list[dict] | None = None,
    blue_synergies: list[dict] | None = None,
    red_synergies: list[dict] | None = None,
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
        lane_lines = "\n".join(
            f"- {l['position']}: {l['blue']} vs {l['red']} — "
            + (
                f"{l['blue_lane_win_rate'] * 100:.0f}% de vitória do azul em "
                f"{l['matchup_games']} confrontos diretos reais"
                if l.get("matchup_games", 0) >= 10
                else "poucos confrontos diretos no histórico, estimativa aproximada"
            )
            for l in lanes
        )
        sections.append(
            f"Matchups por lane — DADO REAL do histórico de partidas, não "
            f"opinião:\n{lane_lines}"
        )

    sig_blue = [s for s in (blue_synergies or []) if s.get("significant")]
    sig_red = [s for s in (red_synergies or []) if s.get("significant")]
    if sig_blue or sig_red:
        syn_lines = "\n".join(
            f"- {s['a']} + {s['b']} (time azul): {s['delta'] * 100:+.1f} pontos "
            "percentuais de sinergia (estatisticamente distinguível de ruído)"
            for s in sig_blue
        ) + "\n" + "\n".join(
            f"- {s['a']} + {s['b']} (time vermelho): {s['delta'] * 100:+.1f} "
            "pontos percentuais de sinergia (estatisticamente distinguível de ruído)"
            for s in sig_red
        )
        sections.append(
            f"Sinergias de dupla com significância estatística — DADO REAL, já "
            f"corrigido por amostra pequena (shrinkage + intervalo de "
            f"confiança):\n{syn_lines.strip()}"
        )

    instructions = (
        "\n\nCom base nisso, escreva uma orientação estratégica curta (4-6 "
        "frases, português do Brasil, texto corrido, sem markdown) para o "
        "time em desvantagem (ou para os dois lados, se a diferença for "
        "pequena) sobre o que costuma ser prioridade numa situação assim — "
        "controle de objetivo, prioridade de rota, quando lutar ou evitar "
        "luta, que tipo de vantagem precisa ser convertida antes que o "
        "adversário se recupere."
    )
    if blue_champions or red_champions:
        instructions += (
            " Cite campeões específicos quando fizer sentido (power spike, "
            "papel na composição, o matchup/sinergia listado acima) em vez de "
            "só falar em 'time azul'/'time vermelho' — mas só cite número de "
            "matchup/sinergia se ele foi listado acima; não invente estatística."
        )
    instructions += (
        " Use conhecimento geral de macro/estratégia de League of Legends "
        "pra tudo que não for dado explícito acima.\n\n"
        "Termine com uma frase curta deixando claro que isso é leitura "
        "estratégica geral aplicada a este estado — não uma recomendação "
        "verificada pelos dados desta partida específica, já que o modelo "
        "não vê itens, posição dos jogadores nem controle de wave."
    )

    prompt = "\n\n".join(sections) + instructions

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
