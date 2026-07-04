"""Coleta de partidas COMPETITIVAS (pro play) — Oracle's Elixir.

Fonte: os CSVs anuais públicos de Tim Sevenhuysen (oracleselixir.com),
padrão em trabalhos acadêmicos de LoL — cobrem LCK/LPL/LEC/LTA/CBLOL
etc., com 12 linhas por jogo (10 jogadores + 2 times) e estatísticas
por corte de tempo (gold/xp/cs diff aos 10/15 min), o que conversa
diretamente com as nossas features de solo queue.

Os arquivos ficam num Google Drive público que tem QUOTA de download:
quando muitos usuários baixam no mesmo dia, o Drive responde "Quota
exceeded" e o download automático falha — nesse caso o script avisa e
o fallback é baixar manualmente em oracleselixir.com/tools/downloads
e salvar em data/pro/ com o nome original.

Uso:  python -m src.collect.collect_pro --year 2026
Gera: data/pro/{year}_LoL_esports_match_data_from_OraclesElixir.csv
Depois: python -m src.etl.load_pro  (carrega no Postgres)
"""
import argparse
import os

import requests

# ids dos arquivos anuais na pasta pública do Drive do Oracle's Elixir
# (extraídos da listagem da pasta 1gLSw0RLjBbtaNy0dgnGQDAZOHIgCe-HH)
DRIVE_FILE_IDS = {
    2023: "1XXk2LO0CsNADBB1LRGOV5rUpyZdEZ8s2",
    2024: "1IjIEhLc9n8eLKeY-yh_YigKVWbhgGBsN",
    2025: "1v6LRphp2kYciU4SXp0PCjEMuev1bDejc",
    2026: "1hnpbrUpBMS1TZI7IovfpKeZfWJH1Aptm",
}


def download_year(year: int) -> str | None:
    if year not in DRIVE_FILE_IDS:
        print(f"Ano {year} não mapeado — anos disponíveis: {sorted(DRIVE_FILE_IDS)}")
        return None
    os.makedirs("data/pro", exist_ok=True)
    dest = f"data/pro/{year}_LoL_esports_match_data_from_OraclesElixir.csv"

    url = (
        "https://drive.usercontent.google.com/download"
        f"?id={DRIVE_FILE_IDS[year]}&export=download&confirm=t"
    )
    print(f"Baixando {year}…")
    resp = requests.get(url, timeout=300)
    body_start = resp.content[:200].decode("utf-8", errors="ignore")
    if resp.status_code != 200 or body_start.lstrip().startswith("<!DOCTYPE"):
        if "Quota exceeded" in resp.text[:2000]:
            print(
                "O Google Drive bloqueou o download por quota (muita gente baixou "
                "hoje). Tente de novo mais tarde, ou baixe manualmente em "
                f"oracleselixir.com/tools/downloads e salve como {dest}"
            )
        else:
            print(f"Falha no download (HTTP {resp.status_code}).")
        return None

    with open(dest, "wb") as f:
        f.write(resp.content)
    print(f"OK: {dest} ({len(resp.content) / 1e6:.1f} MB)")
    return dest


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=2026)
    args = p.parse_args()
    download_year(args.year)
