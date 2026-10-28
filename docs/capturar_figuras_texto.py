"""Captura as figuras que entram NO CORPO do TCC (Seção 5), recortadas por painel.

POR QUE EXISTE (2026-10-28): até aqui as telas iam inteiras para o Anexo A, no
fim do documento. O orientador comentou que, com tudo no fim, o texto perde o
sentido: a Seção 5 diz "ver Figura 2" e o leitor precisa ir até o anexo. Os
aprovados usam figuras compactas junto da discussão. Uma tela inteira (1440 x
2400 px) não cabe no corpo sem estourar o limite de páginas; o painel que o
texto discute, sim.

Recorte por ELEMENTO, não por coordenada: cada figura é a caixa que envolve os
cards nomeados abaixo (localizados pelo título). Se o layout mudar, o recorte
acompanha; coordenada fixa recortaria o lugar errado sem avisar.

Uso (API em :8000 e frontend em :5173, a API antes):
    .venv\\Scripts\\python.exe docs\\capturar_figuras_texto.py

Grava em reports/figuras_texto/ e registra em figuras.json o instante, a base
(partidas na fila 420) e, para a figura da consulta em linguagem natural, a
pergunta e a SQL gerada: são os fatos que a legenda e o texto afirmam.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "reports" / "figuras_texto"
FRONT = os.environ.get("FRONT_URL", "http://localhost:5173")
TEMA = os.environ.get("ANEXO_TEMA", "dark")
MATCH_ID = os.environ.get("ANEXO_MATCH_ID", "NA1_5653867149")
# Pergunta 9 do benchmark do Apêndice B (passa). Usar uma pergunta do próprio
# benchmark deixa a figura conferível contra o quadro, em vez de uma pergunta
# escolhida por ter saído bonita. Uma pergunta fora do benchmark testada em
# 2026-10-28 ("win rate do azul por região") FALHOU (coluna inexistente): os
# 88% são medidos, não garantidos.
PERGUNTA_NLQ = "Quais os 5 campeões mais jogados na posição MIDDLE?"
# Estado da aba Estado do Simulador: vantagem moderada do azul aos 15 min,
# dentro dos ranges de percentil 1-99 de src/lib/matchState.ts
ESTADO = {"gold_diff": "2000", "xp_diff": "1000", "kill_diff": "3",
          "tower_diff": "0", "dragon_diff": "1"}


def _partidas_fila_420() -> int:
    sys.path.insert(0, str(RAIZ))
    from src.db import get_conn

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM matches WHERE queue_id = 420")
        return int(cur.fetchone()[0])


def _card(pagina, titulo: str):
    """O card (div.rounded-xl) cujo título contém `titulo`."""
    return pagina.locator("div.rounded-xl", has=pagina.get_by_text(titulo, exact=False)).last


def _uniao(caixas):
    x0 = min(c["x"] for c in caixas)
    y0 = min(c["y"] for c in caixas)
    x1 = max(c["x"] + c["width"] for c in caixas)
    y1 = max(c["y"] + c["height"] for c in caixas)
    return {"x": x0 - 6, "y": y0 - 6, "width": x1 - x0 + 12, "height": y1 - y0 + 12}


def _recortar(pagina, arquivo: str, titulos: list[str]) -> None:
    caixas = []
    for t in titulos:
        card = _card(pagina, t)
        card.wait_for(state="visible", timeout=30000)
        card.scroll_into_view_if_needed()
        caixas.append(card.bounding_box())
    # bounding_box é relativo à viewport; com viewport alta o bastante para a
    # página inteira, nada rola e a caixa vale para o screenshot direto
    pagina.screenshot(path=str(SAIDA / arquivo), clip=_uniao(caixas))
    kb = (SAIDA / arquivo).stat().st_size / 1024
    if kb < 15:
        raise RuntimeError(f"{arquivo}: recorte suspeito de estar vazio ({kb:.0f} KB)")
    print(f"ok {arquivo} ({kb:.0f} KB)")


def _abrir(contexto, rota: str, espera: str):
    pagina = contexto.new_page()
    pagina.goto(f"{FRONT}{rota}", wait_until="load", timeout=45000)
    pagina.wait_for_selector(f"text={espera}", timeout=30000)
    # Recharts anima as barras; antes disso o recorte sai com o eixo vazio
    # (mesma pegadinha do recapturar_anexo_a.py)
    pagina.wait_for_timeout(4000)
    if pagina.locator("text=Erro no servidor").count() > 0:
        raise RuntimeError(f"{rota}: a página mostrou 'Erro no servidor'")
    return pagina


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    registro = {"tema": TEMA, "match_id": MATCH_ID}
    with sync_playwright() as p:
        # --no-proxy-server: ver o comentário em recapturar_anexo_a.py
        nav = p.chromium.launch(args=["--no-proxy-server"])
        # deviceScaleFactor 2: o recorte vai a ~15 cm de largura no .docx; em
        # escala 1 o texto dos eixos fica serrilhado na impressão
        contexto = nav.new_context(viewport={"width": 1440, "height": 3200},
                                   device_scale_factor=2)
        contexto.add_init_script(f"window.localStorage.setItem('theme', '{TEMA}');")

        pg = _abrir(contexto, "/competitivo", "O viés de lado INVERTE")
        _recortar(pg, "fig_competitivo.png",
                  ["O viés de lado INVERTE", "Ouro aos 15 minutos"])
        pg.close()

        pg = _abrir(contexto, f"/partidas/{MATCH_ID}", "Mapa de calor da partida")
        _recortar(pg, "fig_partida.png",
                  ["Mapa de calor da partida", "Objetivos até"])
        pg.close()

        pg = _abrir(contexto, "/simulador", "Simulador")
        pg.get_by_role("button", name="Estado").first.click()
        pg.wait_for_selector("#gold_diff", timeout=15000)
        for chave, valor in ESTADO.items():
            pg.locator(f"#{chave}").fill(valor)
        # a predição tem debounce de 300 ms e depois o SHAP anima
        pg.wait_for_timeout(4000)
        _recortar(pg, "fig_simulador_estado.png",
                  ["Estado aos 15 minutos", "Contribuição de cada fator"])
        registro["estado_simulador"] = {k: int(v) for k, v in ESTADO.items()}
        prob = pg.locator("[role=meter]").get_attribute("aria-valuenow")
        registro["estado_simulador"]["prob_azul_pct_exibida"] = int(prob) if prob else None
        pg.close()

        pg = _abrir(contexto, "/simulador", "Simulador")
        pg.get_by_role("button", name="Explicabilidade").first.click()
        pg.wait_for_selector("text=Como a importância de cada fator evolui", timeout=30000)
        pg.wait_for_timeout(4000)
        _recortar(pg, "fig_shap_fases.png", ["Como a importância de cada fator evolui"])
        pg.close()

        pg = _abrir(contexto, "/consulta", "Pergunte aos dados")
        pg.get_by_placeholder("Ex.: qual posição").fill(PERGUNTA_NLQ)
        pg.get_by_role("button", name="Perguntar").click()
        # a tabela do resultado é o sinal de que a SQL rodou no banco
        pg.wait_for_selector("table", timeout=120000)
        pg.get_by_role("button", name="SQL", exact=True).click()
        pg.wait_for_timeout(1500)
        sql = pg.locator("pre").first.inner_text()
        card = pg.locator("div.rounded-xl", has=pg.locator("table")).first
        box = card.bounding_box()
        pg.screenshot(path=str(SAIDA / "fig_nlq.png"), clip=_uniao([box]))
        print(f"ok fig_nlq.png ({(SAIDA / 'fig_nlq.png').stat().st_size / 1024:.0f} KB)")
        registro["nlq"] = {"pergunta": PERGUNTA_NLQ, "sql_gerada": sql}
        pg.close()
        nav.close()

    registro["capturado_em"] = datetime.now().isoformat(timespec="seconds")
    registro["base_partidas_fila_420"] = _partidas_fila_420()
    (SAIDA / "figuras.json").write_text(
        json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"registro: figuras.json (base {registro['base_partidas_fila_420']} partidas)")


if __name__ == "__main__":
    main()
