"""Recaptura as telas do Anexo A contra a API e o frontend de producao.

POR QUE RECAPTURAR: as capturas de 2026-09-28 foram feitas com 24.154 partidas
no banco. A coleta posterior levou a base a 39.426, e a Figura 2 (Dashboard)
passou a mostrar a tabela regional com NA1 = 1.446 enquanto o texto da Secao
5.3 afirma 7.159 — contradicao visivel dentro do proprio documento.

Uso (API em :8000 e frontend em :5173):
    .venv\\Scripts\\python.exe docs\\recapturar_anexo_a.py

Grava: reports/anexo_a/captura.json — `capturado_em`, `base_partidas_fila_420`,
as telas e o id de partida usado. E o arquivo que o Anexo A do TCC cita para
sustentar "N partidas no momento da captura": antes disso a afirmacao se
apoiava so no mtime do PNG, que este proprio comando invalida.
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "reports" / "anexo_a"
FRONT = os.environ.get("FRONT_URL", "http://localhost:5173")
ALTURA = 2400


def _partidas_fila_420() -> int:
    """Partidas na fila ranqueada no momento da captura.

    POR QUE ISTO ENTROU NO SCRIPT: o Anexo A afirmava "39.426 partidas no
    momento da captura, as mesmas da Seção 5.3", e a unica fonte dessa
    afirmacao era o mtime do PNG — que o proprio comando de regeneracao
    invalida, sem que nada acuse. Um anexo que descreve o estado do banco sem
    registrar o estado do banco e um anexo que nao sabe o que mostra.
    """
    sys.path.insert(0, str(RAIZ))
    from src.db import get_conn

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM matches WHERE queue_id = 420")
        return int(cur.fetchone()[0])

# (arquivo, caminho, espera) — a espera é pelo dado, não por tempo fixo:
# o dashboard só sai depois da consulta ao banco.
TELAS = [
    ("01_inicio.png", "/", "text=Início"),
    ("02_dashboard.png", "/dashboard", "text=Vitória"),
    # /campeoes é a LISTA; o detalhe (que tem itens e matchups, o que
    # interessa ao Anexo A) fica em /campeoes/:name. Jayce é o campeã com
    # mais jogos na base (7.017) e é justamente o usado na seção de
    # verificação do diário (itens e win rate conferidos contra SQL direto).
    ("03_campeoes.png", "/campeoes/Jayce", "text=Itens finalizados"),
    # /partidas NÃO é rota: App.tsx redireciona para "/" (rota legada).
    # A análise de partida vive em /partidas/:id, e o id precisa existir de
    # fato no banco — um id inventado renderiza o banner de erro e a trava
    # de segurança abaixo rejeita a captura.
    ("04_partida_detalhe.png",
     f"/partidas/{os.environ.get('ANEXO_MATCH_ID', 'NA1_5653867149')}",
     "text=Análise"),
    ("05_competitivo.png", "/competitivo", "text=Competitivo"),
    ("06_simulador.png", "/simulador", "text=Simulador"),
]


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    erros = []
    with sync_playwright() as p:
        # --no-proxy-server é obrigatório NESTA MÁQUINA: sem ele o Chromium
        # headless não alcança http://localhost:8000 e renderiza o banner
        # "Erro no servidor — Não foi possível conectar à API". O ProxyEnable
        # do Windows está 0, mas o Chromium ainda herda a configuração de
        # `<local>` e o fetch falha. Confirmado: com a flag, HTTP 200.
        nav = p.chromium.launch(args=["--no-proxy-server"])
        for nome, rota, espera in TELAS:
            pagina = nav.new_page(viewport={"width": 1440, "height": ALTURA})
            try:
                pagina.goto(f"{FRONT}{rota}", wait_until="networkidle", timeout=45000)
                pagina.wait_for_selector(espera, timeout=25000)
                # Recharts + full_page=True = barras vazias no screenshot. A
                # animação não completa antes do corte e o axes sai sem os
                # retângulos (pegadinha do diário em 2026-07-02). Esperar o
                # seletor `.recharts-bar-rectangle path` NÃO resolve — o
                # elemento existe na altura 0 durante a animação.
                # Solução: viewport alta o bastante para a página inteira
                # caber, e screenshot SEM full_page.
                altura_real = pagina.evaluate(
                    "() => Math.max(document.body.scrollHeight,"
                    " document.documentElement.scrollHeight)")
                if altura_real > ALTURA:
                    pagina.set_viewport_size({"width": 1440, "height": int(altura_real) + 200})
                    pagina.wait_for_timeout(2500)
                pagina.wait_for_timeout(6000)
                # TRAVA DE SEGURANÇA: a primeira versão deste script reportava
                # "ok" e gravava a tela de ERRO da API — os seletores das telas
                # com pouco texto (uma tabela vazia com o header) ainda apareciam
                # mesmo com a API fora. Um arquivo de 24 KB era o sintoma.
                # Agora, se o banner de erro estiver na tela, a captura é
                # rejeitada em vez de virar figura do TCC.
                if pagina.locator("text=Erro no servidor").count() > 0:
                    raise RuntimeError("a página mostrou 'Erro no servidor' — "
                                       "a API não respondeu no navegador")
                arquivo = SAIDA / nome
                pagina.screenshot(path=str(arquivo))
                kb = arquivo.stat().st_size / 1024
                if kb < 60:
                    raise RuntimeError(f"captura suspeita de estar vazia ({kb:.0f} KB)")
                print(f"ok {nome} <- {rota}  ({kb:.0f} KB)")
            except Exception as exc:
                erros.append(f"{nome}: {type(exc).__name__} {str(exc)[:90]}")
                print(f"FALHA {nome}: {str(exc)[:130]}")
            finally:
                pagina.close()
                time.sleep(0.4)
        nav.close()
    if erros:
        print("\n--- falhas ---")
        for e in erros:
            print(" ", e)
        # Nao grava captura.json com falhas parciais: o Anexo A cita este
        # arquivo, e um registro de seis telas das quais tres falharam seria
        # pior do que nenhum registro.
        raise SystemExit(1)

    # O registro que o Anexo A cita. Sem ele, a afirmacao "N partidas no
    # momento da captura" so se sustenta pelo mtime do PNG, que qualquer
    # regeracao posterior torna falso sem aviso.
    base = _partidas_fila_420()
    registro = {
        "capturado_em": datetime.now().isoformat(timespec="seconds"),
        "base_partidas_fila_420": base,
        "telas": [{"arquivo": nome, "rota": rota} for nome, rota, _ in TELAS],
        "match_id_usado": os.environ.get("ANEXO_MATCH_ID", "NA1_5653867149"),
    }
    (SAIDA / "captura.json").write_text(
        json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n6 capturas regravadas em {SAIDA}")
    print(f"registro: captura.json (base {base} partidas)")


if __name__ == "__main__":
    main()