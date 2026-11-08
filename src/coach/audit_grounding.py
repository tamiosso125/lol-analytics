"""Auditoria de fundamentação do coach: a IA inventa estatística? (2026-11-04)

O texto do TCC (Seção 4.7) afirma que cada resposta do coach separa o que vem
dos dados do que é conhecimento geral, e o AGENTS.md (invariante 2) exige que
nenhum número apareça sem ter sido calculado do histórico. Até aqui isso foi
verificado só à mão (auditorias de 2026-07-08 e 2026-11-03 no diário). Este
script mede de forma repetível.

Método. Cada caso passa pelo MESMO caminho do produto (`/predict`, `/compose`,
`/coach`, em processo, via TestClient). Um espião no cliente da Anthropic
guarda o prompt exato de cada chamada. Os dados fornecidos à IA são o prompt
sem o bloco de instruções ("Com base nisso, escreva..."), porque as instruções
trazem números ("4-8 frases") que não são dado e poderiam mascarar uma
invenção. Todo número da narrativa tem que estar nos dados fornecidos, com
tolerância de 0,51 para porcentagem (a narrativa arredonda). O que não bater é
SINALIZADO e revisado à mão; o resultado oficial usa a revisão, não só o
automático.

O que NÃO mede: se o conhecimento geral está marcado como tal (não dá para
automatizar) nem se o conhecimento geral está certo. Só estatística numérica,
a presença da ressalva final e a origem dos itens sugeridos.

Casos: partidas reais do banco (ordem estável por hash do match_id), três
modos do produto em rodízio e os cortes 15, 20 e 25:
  completo     estado + composição + contexto tático da partida (análise de partida)
  composicao   estado + composição, sem partida (Simulador com campeões)
  so_estado    só o estado (Simulador, aba Estado)

A saída da IA varia entre execuções (temperatura 0,4): rode uma vez e guarde a
saída bruta (`reports/coach_audit.json`), que é o que o TCC cita.

Uso:  python -m src.coach.audit_grounding --n 36
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))

SAIDA = RAIZ / "reports" / "coach_audit.json"
FEATURES = ["gold_diff", "xp_diff", "kill_diff", "tower_diff", "dragon_diff"]
POSICOES = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
MODOS = ["completo", "composicao", "so_estado"]
CORTES = [15, 20, 25]
DIVISOR_INSTRUCOES = "Com base nisso, escreva"

RE_NUM = re.compile(r"(?<![\w.])\d{1,3}(?:\.\d{3})+(?:,\d+)?|(?<![\w.])\d+(?:[.,]\d+)?")


def _valor(token: str) -> float:
    # "2.100" é milhar, mas "0.049" é decimal (valor de SHAP); o prompt usa ponto decimal
    if re.fullmatch(r"[1-9]\d{0,2}(?:\.\d{3})+(?:,\d+)?", token):
        return float(token.replace(".", "").replace(",", "."))
    return float(token.replace(",", "."))


# tempo de jogo ("5-10 minutos", "aos 20 min") e formato ("5v5") são conhecimento geral
# de League of Legends, não estatística do histórico: contados à parte, não sinalizados
RE_TEMPO = re.compile(r"^(?:\s*[-\u2013]\s*\d+)?\s*(?:min|minutos?)\b")
RE_FORMATO = re.compile(r"^v\d")


def numeros_da_narrativa(texto: str) -> list[dict]:
    """Cada número do texto com o contexto, se é porcentagem e o valor."""
    saida = []
    for m in RE_NUM.finditer(texto):
        fim = m.end()
        resto = texto[fim:fim + 3]
        if resto[:1] in ("ª", "º"):  # ordinal ("1ª torre")
            continue
        seguinte = texto[fim:fim + 30]
        saida.append({
            "token": m.group(0),
            "valor": _valor(m.group(0)),
            "tempo_ou_formato": bool(RE_TEMPO.match(seguinte) or RE_FORMATO.match(seguinte)),
            "percentual": texto[fim:fim + 2].strip().startswith("%"),
            "contexto": texto[max(0, m.start() - 30):fim + 30].replace("\n", " "),
        })
    return saida


def numeros_dos_dados(dados: str) -> list[float]:
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", dados)]


def sinalizados(narrativa: str, dados: str) -> tuple[int, int, list[dict]]:
    """(números no total, de tempo/formato, os sem correspondente nos dados)."""
    ref = numeros_dos_dados(dados)
    itens = numeros_da_narrativa(narrativa)
    fora = []
    for n in itens:
        if n["tempo_ou_formato"]:
            continue
        tol = 0.51 if n["percentual"] else 0.0
        if not any(abs(n["valor"] - p) <= tol for p in ref):
            fora.append(n)
    return len(itens), sum(1 for n in itens if n["tempo_ou_formato"]), fora


def ressalva_final(narrativa: str) -> bool:
    ultima = re.split(r"(?<=[.!?])\s+", narrativa.strip())[-1].lower()
    # heurística: a última frase fala dos limites da leitura. As 36 são lidas à mão depois.
    return any(k in ultima for k in ("geral", "aproximada", "verificad", "observável", "observavel",
                                     "wave", "minion", "não substitui"))


RE_CONTAGEM = re.compile(r"\s*(?:jogos|partidas|vezes|vitórias|derrotas)\b")


def conferencia_estrita(narrativa: str, dados: str) -> dict:
    """Segunda checagem, mais rígida que `sinalizados`.

    Um número da narrativa pode "passar" só por coincidir com outro número
    qualquer do prompt. Aqui cada porcentagem tem que bater com uma porcentagem
    DOS DADOS (ou com o complemento a 100, a probabilidade do outro time) e cada
    contagem de jogos ou partidas com uma contagem de jogos ou partidas dos dados.
    """
    pcts = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", dados)]
    pcts_ref = set(pcts) | {round(100 - x, 1) for x in pcts}
    jogos = {float(x) for x in re.findall(r"(\d+)\s*(?:jogos|partidas)", dados)}
    r = {"percentuais": 0, "percentuais_sem_correspondente": [], "contagens": 0,
         "contagens_sem_correspondente": []}
    for m in RE_NUM.finditer(narrativa):
        v = _valor(m.group(0))
        ctx = narrativa[max(0, m.start() - 30):m.end() + 25].replace("\n", " ")
        if narrativa[m.end():m.end() + 2].strip().startswith("%"):
            r["percentuais"] += 1
            if not any(abs(v - x) <= 0.51 for x in pcts_ref):
                r["percentuais_sem_correspondente"].append({"token": m.group(0), "contexto": ctx})
        elif RE_CONTAGEM.match(narrativa[m.end():m.end() + 14]):
            r["contagens"] += 1
            if v not in jogos:
                r["contagens_sem_correspondente"].append({"token": m.group(0), "contexto": ctx})
    return r


def metricas_do_caso(narrativa: str, prompt: str) -> dict:
    """Tudo que se calcula só a partir da narrativa e do prompt gravados."""
    dados = prompt.split(DIVISOR_INSTRUCOES)[0]
    total, tempo, fora = sinalizados(narrativa, dados)
    return {"n_numeros": total, "n_tempo_ou_formato": tempo, "sinalizados": fora,
            "ressalva_final": ressalva_final(narrativa), "estrito": conferencia_estrita(narrativa, dados)}


def resumir(casos: list[dict]) -> dict:
    return {
        "casos": len(casos),
        "numeros_total": sum(c["n_numeros"] for c in casos),
        "numeros_tempo_ou_formato": sum(c["n_tempo_ou_formato"] for c in casos),
        "numeros_sinalizados": sum(len(c["sinalizados"]) for c in casos),
        "casos_com_sinalizado": sum(1 for c in casos if c["sinalizados"]),
        "percentuais": sum(c["estrito"]["percentuais"] for c in casos),
        "percentuais_sem_correspondente": sum(len(c["estrito"]["percentuais_sem_correspondente"]) for c in casos),
        "contagens_de_jogos": sum(c["estrito"]["contagens"] for c in casos),
        "contagens_sem_correspondente": sum(len(c["estrito"]["contagens_sem_correspondente"]) for c in casos),
        "ressalva_final_heuristica": sum(1 for c in casos if c["ressalva_final"]),
        "itens_sugeridos": sum(len(c["itens_sugeridos"]) for c in casos),
        "itens_nos_dados_fornecidos": sum(1 for c in casos for i in c["itens_sugeridos"] if i["nos_dados_fornecidos"]),
        "por_modo": {m: sum(1 for c in casos if c["modo"] == m) for m in MODOS},
    }


def reanalisar() -> None:
    """Recalcula as métricas sobre a saída JÁ gravada, sem chamar o modelo.

    Serve para mudar uma regra do detector (e para o `verifica_tcc.py` conferir
    o número) sem refazer as 36 respostas, que variam a cada execução."""
    dados = json.loads(SAIDA.read_text(encoding="utf-8"))
    for c in dados["casos"]:
        c.update(metricas_do_caso(c["narrativa"], c["prompt"]))
    dados["resumo"] = resumir(dados["casos"])
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(dados["resumo"], ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=36)
    ap.add_argument("--reanalisar", action="store_true", help="só recalcula as métricas da saída gravada")
    args = ap.parse_args()
    if args.reanalisar:
        reanalisar()
        return

    import anthropic
    from fastapi.testclient import TestClient

    from src.api.main import _items, app
    from src.db import get_conn
    from src.features.build_features import features_from_timeline

    chamadas: list[dict] = []
    real = anthropic.Anthropic

    class Espiao:
        """Guarda prompt e texto de cada chamada, sem alterar o comportamento."""

        def __init__(self, *a, **k):
            self._c = real(*a, **k)
            self.messages = self

        def create(self, **kw):
            r = self._c.messages.create(**kw)
            texto = "".join(getattr(b, "text", "") for b in r.content)
            chamadas.append({"prompt": kw["messages"][0]["content"], "texto": texto, "stop": r.stop_reason})
            return r

    anthropic.Anthropic = Espiao
    cliente = TestClient(app)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT m.match_id FROM matches m JOIN raw_timelines t USING (match_id)
           WHERE m.queue_id = 420 AND m.game_duration_s >= 1560
           ORDER BY md5(m.match_id) LIMIT %s""",
        (args.n * 3,),
    )
    candidatos = [r[0] for r in cur.fetchall()]

    casos = []
    for match_id in candidatos:
        if len(casos) >= args.n:
            break
        i = len(casos)
        modo, corte = MODOS[i % 3], CORTES[(i // 3) % 3]
        cur.execute("SELECT payload FROM raw_timelines WHERE match_id = %s", (match_id,))
        payload = cur.fetchone()[0]
        feats = features_from_timeline(payload, corte)
        if feats is None:
            continue
        estado = {f: feats[f] for f in FEATURES}
        estado["minute"] = corte
        pred = cliente.post("/predict", json=estado)
        if pred.status_code != 200:
            print(match_id, "predict", pred.status_code)
            continue
        pj = pred.json()
        corpo = {"state": estado, "blue_win_probability": pj["blue_win_probability"],
                 "shap_contributions": pj["shap_contributions"],
                 "shap_base_value": pj.get("shap_base_value")}
        if modo in ("completo", "composicao"):
            cur.execute(
                "SELECT team_id, team_position, champion_name FROM participants "
                "WHERE match_id = %s AND team_position = ANY(%s)", (match_id, POSICOES))
            azul, verm = {}, {}
            for tid, pos, champ in cur.fetchall():
                (azul if tid == 100 else verm)[pos] = champ
            if len(azul) < 5 or len(verm) < 5:
                continue
            comp = cliente.post("/compose", json={"blue": azul, "red": verm})
            if comp.status_code != 200:
                print(match_id, "compose", comp.status_code)
                continue
            cj = comp.json()
            corpo.update(blue_champions=azul, red_champions=verm, lanes=cj["lanes"],
                         blue_synergies=cj["synergies"]["blue"], red_synergies=cj["synergies"]["red"])
        if modo == "completo":
            corpo.update(match_id=match_id, game_minute=corte)

        chamadas.clear()
        resp = cliente.post("/coach", json=corpo)
        if resp.status_code != 200 or not chamadas:
            print(match_id, "coach", resp.status_code, resp.text[:120])
            continue
        rj = resp.json()
        dados = chamadas[0]["prompt"].split(DIVISOR_INSTRUCOES)[0]
        met = metricas_do_caso(rj["narrative"], chamadas[0]["prompt"])
        total, fora = met["n_numeros"], met["sinalizados"]

        itens = []
        for s in rj["build_suggestions"]:
            for iid in s["items"]:
                nome = _items[str(iid)]["name"]
                itens.append({"campeao": s["champion"], "item": nome, "nos_dados_fornecidos": nome in dados})
        casos.append({
            "n": i + 1, "match_id": match_id, "modo": modo, "corte": corte,
            "narrativa": rj["narrative"], **met, "itens_sugeridos": itens,
            "stop_reason": chamadas[0]["stop"], "prompt": chamadas[0]["prompt"],
        })
        print(f"{len(casos):2d}/{args.n} {modo:<10} {corte} min  números {total:2d}  sinalizados {len(fora)}  "
              f"ressalva {'ok' if casos[-1]['ressalva_final'] else 'NÃO'}", flush=True)

    anthropic.Anthropic = real
    resumo = resumir(casos)
    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(json.dumps({
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "modelo": "claude-haiku-4-5-20251001", "temperatura": 0.4,
        "metodo": "numeros da narrativa contra os dados do prompt (sem instrucoes); sinalizados revisados a mao",
        "resumo": resumo, "casos": casos,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n", json.dumps(resumo, ensure_ascii=False))
    print("->", SAIDA)


if __name__ == "__main__":
    main()
