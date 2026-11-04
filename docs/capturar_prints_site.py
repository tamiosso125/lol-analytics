"""Prints do site em 16:9 para slides, plano B da demonstração e material de apoio.

Diferente de `capturar_figuras_texto.py` (recortes para o corpo do TCC) e de
`recapturar_anexo_a.py` (telas inteiras do Apêndice F), aqui cada print é a
janela de 1920 x 1080, rolada até o painel que importa, no formato de um slide.
Não alimenta o TCC: nenhuma figura do texto depende deste script.

Cobre as telas e as funções que os outros dois não mostram: composição 5x5 do
Simulador, aba Explicabilidade, lista de campeões, mapa de calor e objetivos da
partida, os dois gráficos do Competitivo, perfil de jogador profissional e a
consulta em linguagem natural com uma pergunta do solo queue e outra do
competitivo. Nenhum perfil de jogador do solo queue é capturado: são pessoas
reais, e o resumo de rankings já mostra o que a apresentação precisa.

Uso (API em :8000 e frontend em :5173, a API antes):
    .venv\\Scripts\\python.exe docs\\capturar_prints_site.py

Grava em reports/prints_site/ e registra em prints.json o instante e a base.
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
TEMA = os.environ.get("PRINTS_TEMA", "dark")  # "dark" ou "light"
SAIDA = RAIZ / "reports" / "prints_site" / ("" if TEMA == "dark" else "claro")
FRONT = os.environ.get("FRONT_URL", "http://localhost:5173")
MATCH_ID = os.environ.get("ANEXO_MATCH_ID", "NA1_5653867149")
LARGURA, ALTURA = 1920, 1080

PERGUNTA_SOLO = "Quais os 5 campeões mais jogados na posição MIDDLE?"
PERGUNTA_PRO = "Quantos jogos profissionais de 2026 existem no banco?"
ESTADO = {"gold_diff": "2000", "xp_diff": "1000", "kill_diff": "3",
          "tower_diff": "0", "dragon_diff": "1"}
AZUL = ["Jayce", "Lee Sin", "Ahri", "Jinx", "Thresh"]
VERMELHO = ["Gnar", "Viego", "Syndra", "Ezreal", "Nautilus"]


def _base() -> int:
    sys.path.insert(0, str(RAIZ))
    from src.db import get_conn

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM matches WHERE queue_id = 420")
        return int(cur.fetchone()[0])


def _puuid_destaque() -> str | None:
    import urllib.request

    try:
        with urllib.request.urlopen("http://localhost:8000/stats/highlights", timeout=20) as r:
            d = json.load(r)
        bp = d.get("best_player") or {}
        return bp.get("puuid") if not bp.get("name") else None
    except Exception:  # noqa: BLE001
        return None


def _abrir(contexto, rota: str, espera: str):
    pg = contexto.new_page()
    pg.goto(f"{FRONT}{rota}", wait_until="load", timeout=45000)
    pg.wait_for_selector(f"text={espera}", timeout=30000)
    pg.wait_for_timeout(3500)  # Recharts anima as barras
    if pg.locator("text=Erro no servidor").count() > 0:
        raise RuntimeError(f"{rota}: a página mostrou 'Erro no servidor'")
    return pg


def _rolar(pg, pixels: int = 960) -> None:
    """Segunda janela da página: a roda do mouse rola o contêiner certo, seja a
    janela ou o `main` do layout (scrollIntoView não rolava, os prints saíam
    idênticos ao de cima, conferido por hash em 2026-11-03)."""
    pg.mouse.move(LARGURA // 2, ALTURA // 2)
    pg.mouse.wheel(0, pixels)
    pg.wait_for_timeout(1500)


def _salvar(pg, nome: str, minimo_kb: int = 40) -> None:
    arquivo = SAIDA / nome
    pg.screenshot(path=str(arquivo))
    kb = arquivo.stat().st_size / 1024
    if kb < minimo_kb:
        raise RuntimeError(f"{nome}: print suspeito de estar vazio ({kb:.0f} KB)")
    print(f"ok {nome} ({kb:.0f} KB)", flush=True)


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    feitos, falhas = [], []

    def tarefa(nome, rota, espera, acao=None):
        pg = None
        try:
            pg = _abrir(CTX, rota, espera)
            if acao:
                acao(pg)
            _salvar(pg, nome)
            feitos.append({"arquivo": nome, "rota": rota})
        except Exception as exc:  # noqa: BLE001
            falhas.append(f"{nome}: {type(exc).__name__} {str(exc)[:110]}")
            print(f"FALHA {nome}: {str(exc)[:130]}", flush=True)
        finally:
            if pg:
                pg.close()
            time.sleep(0.3)

    with sync_playwright() as p:
        nav = p.chromium.launch(args=["--no-proxy-server"])
        CTX = nav.new_context(viewport={"width": LARGURA, "height": ALTURA})
        CTX.add_init_script(f"window.localStorage.setItem('theme', '{TEMA}');")

        tarefa("10_inicio.png", "/", "Início", lambda pg: (pg.wait_for_selector("text=Maior win rate", timeout=30000), pg.wait_for_timeout(5000)))
        tarefa("11_dashboard_topo.png", "/dashboard", "Vitória")
        tarefa("12_dashboard_baixo.png", "/dashboard", "Vitória",
               lambda pg: _rolar(pg))
        tarefa("13_campeoes_lista.png", "/campeoes", "Campe", lambda pg: (pg.wait_for_selector("text=Jayce", timeout=30000), pg.wait_for_timeout(3000)))
        tarefa("14_campeao_detalhe.png", "/campeoes/Jayce", "Itens finalizados")
        tarefa("15_competitivo_vies.png", "/competitivo", "O viés de lado INVERTE")
        tarefa("16_competitivo_baixo.png", "/competitivo", "O viés de lado INVERTE",
               lambda pg: _rolar(pg))
        tarefa("17_partida_mapa.png", f"/partidas/{MATCH_ID}", "Mapa de calor da partida",
               lambda pg: _rolar(pg, 0))
        tarefa("18_partida_baixo.png", f"/partidas/{MATCH_ID}", "Mapa de calor da partida",
               lambda pg: _rolar(pg))

        def composicao(pg):
            pg.wait_for_selector("input[placeholder='— escolher —']", timeout=30000)
            campos = pg.get_by_placeholder("— escolher —")
            n = campos.count()
            if n < 10:
                raise RuntimeError(f"esperava 10 campos de campeão, achei {n}")
            # a ordem no DOM é azul 1 a 5, depois vermelho 1 a 5; se não for,
            # o print continua válido (os dois times aparecem preenchidos)
            # ordem do DOM: por lane, azul e depois vermelho (topo, selva, meio,
            # atirador, suporte)
            intercalado = [c for par in zip(AZUL, VERMELHO) for c in par]
            for i, nome in enumerate(intercalado):
                # nth(i), não first: o placeholder continua no campo depois de
                # preenchido e `.first` reescrevia sempre o primeiro (2026-11-03)
                campo = pg.get_by_placeholder("— escolher —").nth(i)
                campo.click()
                campo.fill(nome)
                pg.wait_for_timeout(250)
                campo.press("Enter")
                pg.wait_for_timeout(300)
            pg.get_by_role("button", name="Analisar confronto").click()
            pg.wait_for_timeout(6000)  # matchups e sinergias vêm da API

        tarefa("19_simulador_composicao.png", "/simulador", "Simulador", composicao)

        def estado(pg):
            pg.get_by_role("button", name="Estado").first.click()
            pg.wait_for_selector("#gold_diff", timeout=15000)
            for chave, valor in ESTADO.items():
                pg.locator(f"#{chave}").fill(valor)
            pg.wait_for_timeout(4000)

        tarefa("20_simulador_estado.png", "/simulador", "Simulador", estado)

        def explic(pg):
            pg.get_by_role("button", name="Explicabilidade").first.click()
            pg.wait_for_selector("text=Como a importância de cada fator evolui", timeout=30000)
            pg.wait_for_timeout(4000)

        tarefa("21_simulador_explicabilidade.png", "/simulador", "Simulador", explic)

        def consulta(pergunta):
            def f(pg):
                pg.get_by_placeholder("Ex.: qual posição").fill(pergunta)
                pg.get_by_role("button", name="Perguntar").click()
                pg.wait_for_selector("table", timeout=120000)
                pg.get_by_role("button", name="SQL", exact=True).click()
                pg.wait_for_timeout(2500)
            return f

        tarefa("22_consulta_solo.png", "/consulta", "Pergunte aos dados", consulta(PERGUNTA_SOLO))
        tarefa("23_consulta_competitivo.png", "/consulta", "Pergunte aos dados", consulta(PERGUNTA_PRO))
        tarefa("24_jogador_profissional.png", "/competitivo/jogadores/Faker", "Faker")

        def explicacao(pg):
            pg.get_by_placeholder("Ex.: qual posição").fill(PERGUNTA_SOLO)
            pg.get_by_role("button", name="Perguntar").click()
            pg.wait_for_selector("table", timeout=120000)
            pg.get_by_role("button", name="Explicação", exact=True).click()
            # o texto vem de uma segunda chamada ao modelo de linguagem
            pg.wait_for_selector("text=Leitura de jogo", timeout=120000) if False else pg.wait_for_timeout(15000)

        tarefa("25_consulta_explicacao.png", "/consulta", "Pergunte aos dados", explicacao)

        # jogador do solo queue: o destaque do Início (o de melhor taxa de vitória),
        # cujo Riot ID não está no banco, então a página não mostra nome nenhum
        puuid = _puuid_destaque()
        if puuid:
            tarefa("26_jogador_solo.png", f"/jogadores/{puuid}", "Jogador")
        nav.close()

    registro = {"capturado_em": datetime.now().isoformat(timespec="seconds"),
                "base_partidas_fila_420": _base(), "viewport": [LARGURA, ALTURA],
                "match_id": MATCH_ID, "prints": feitos, "falhas": falhas}
    (SAIDA / "prints.json").write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(feitos)} prints, {len(falhas)} falhas -> {SAIDA}")
    if falhas:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
