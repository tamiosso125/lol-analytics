"""Orientação estratégica gerada por LLM a partir do estado da partida.

Camada 1 do plano "conhecimento geral aplicado à predição" (ver
docs/diario_execucao.md): o modelo ML já diz QUAL a probabilidade e
QUAL fator pesa mais (SHAP) — isso aqui traduz esses números em
orientação de jogo usando o conhecimento geral de League of Legends da
própria LLM. Mesma convenção de honestidade do "Leitura de jogo:" do
NLQ (src/nlq/nl_to_sql.py): claramente separado do dado observado, e
o prompt força a LLM a dizer explicitamente que não é verificado pelos
dados desta partida — o modelo de ML não vê itens, posição de jogador
nem estado de wave/minion (a API da Riot não grava nada disso).
"""
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
) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    state_lines = "\n".join(
        f"- {FEATURE_LABELS[f]}: {state[f]:+.0f}" for f in FEATURE_LABELS
    )
    shap_lines = "\n".join(
        f"- {FEATURE_LABELS[f]}: {shap_contributions.get(f, 0.0):+.3f}"
        for f in FEATURE_LABELS
    )

    prompt = (
        f"Você é um analista estratégico de League of Legends. Um modelo de "
        f"machine learning avalia uma partida aos {state['minute']} minutos "
        f"(valores azul menos vermelho):\n\n"
        f"Estado:\n{state_lines}\n\n"
        f"Probabilidade de vitória do time azul segundo o modelo: "
        f"{blue_win_probability * 100:.1f}%\n\n"
        f"Contribuição de cada fator para essa predição (SHAP — positivo "
        f"empurra a favor do azul, negativo a favor do vermelho):\n{shap_lines}\n\n"
        "Com base nesse estado, escreva uma orientação estratégica curta "
        "(4-6 frases, português do Brasil, texto corrido, sem markdown) "
        "para o time em desvantagem (ou para os dois lados, se a diferença "
        "for pequena) sobre o que costuma ser prioridade numa situação "
        "assim — controle de objetivo, prioridade de rota, quando lutar ou "
        "evitar luta, que tipo de vantagem precisa ser convertida antes que "
        "o adversário se recupere. Use conhecimento geral de macro/"
        "estratégia de League of Legends, não invente números específicos "
        "desta partida que não foram te dados.\n\n"
        "Termine com uma frase curta deixando claro que isso é leitura "
        "estratégica geral aplicada a este estado — não uma recomendação "
        "verificada pelos dados desta partida, já que o modelo não vê "
        "itens, posição dos jogadores nem controle de wave."
    )

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()
