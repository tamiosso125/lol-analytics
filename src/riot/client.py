"""Cliente da Riot Games API com rate limiting e retry.

Limites da chave de desenvolvimento: 20 req/1s e 100 req/120s.
O cliente usa janela deslizante e respeita o header Retry-After em 429.

Multi-região (planejamento v2, sprint 5): cada instância de RiotClient
é presa a UMA plataforma (ex.: br1, kr, euw1) — os endpoints de liga
(challenger/grandmaster/master) são por plataforma; os de match-v5 são
por REGIÃO de roteamento (americas/asia/europe/sea), derivada
automaticamente da plataforma. Sem argumentos, usa RIOT_PLATFORM/
RIOT_REGION do .env (comportamento de sempre, só BR).
"""
import time
from collections import deque

import requests

from src.config import RIOT_API_KEY, RIOT_PLATFORM, RIOT_REGION

# plataforma -> região de roteamento do match-v5 (accounts/matches/timelines).
# Riot roteia por região, não por plataforma, para esses endpoints.
PLATFORM_TO_REGION = {
    "br1": "americas", "la1": "americas", "la2": "americas",
    "na1": "americas", "oc1": "sea",
    "kr": "asia", "jp1": "asia",
    "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe",
    "ph2": "sea", "sg2": "sea", "th2": "sea", "tw2": "sea", "vn2": "sea",
}


def region_for_platform(platform: str) -> str:
    try:
        return PLATFORM_TO_REGION[platform.lower()]
    except KeyError:
        raise ValueError(
            f"Plataforma '{platform}' não mapeada — adicione em PLATFORM_TO_REGION "
            "(src/riot/client.py) antes de usar."
        )


class RiotClient:
    def __init__(
        self,
        platform: str | None = None,
        region: str | None = None,
        requests_per_2min: int = 95,
    ):
        self.platform = platform or RIOT_PLATFORM
        self.region = region or (region_for_platform(self.platform) if platform else RIOT_REGION)
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": RIOT_API_KEY})
        self.limit = requests_per_2min
        self.window: deque[float] = deque()

    # ---------------- rate limiting ----------------
    # nota: a janela é POR INSTÂNCIA — duas plataformas que roteiam para a
    # mesma região (ex.: br1 e na1, ambas "americas") têm, na prática, o
    # mesmo limite da Riot para os endpoints de match-v5; instanciar um
    # RiotClient por plataforma é uma simplificação de engenharia, não uma
    # garantia de nunca tomar 429 ao coletar várias plataformas da mesma
    # região em paralelo. Sequencial (como collect_matches faz) evita isso.
    def _throttle(self) -> None:
        now = time.time()
        while self.window and now - self.window[0] > 120:
            self.window.popleft()
        if len(self.window) >= self.limit:
            sleep_for = 120 - (now - self.window[0]) + 0.5
            time.sleep(max(sleep_for, 0))
        self.window.append(time.time())

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        for attempt in range(5):
            self._throttle()
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 10))
                print(f"429 rate limit — aguardando {wait}s")
                time.sleep(wait)
                continue
            if resp.status_code in (500, 502, 503, 504):
                time.sleep(2**attempt)
                continue
            resp.raise_for_status()
        raise RuntimeError(f"Falha após retries: {url}")

    # ---------------- endpoints (por plataforma) ----------------
    def challenger_league(self, queue: str = "RANKED_SOLO_5x5") -> dict:
        url = f"https://{self.platform}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}"
        return self._get(url)

    def grandmaster_league(self, queue: str = "RANKED_SOLO_5x5") -> dict:
        url = f"https://{self.platform}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{queue}"
        return self._get(url)

    def master_league(self, queue: str = "RANKED_SOLO_5x5") -> dict:
        url = f"https://{self.platform}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{queue}"
        return self._get(url)

    # ---------------- endpoints (por região de roteamento) ----------------
    def account_by_puuid(self, puuid: str) -> dict:
        """gameName/tagLine de um jogador (account-v1) — o endpoint de
        liga não retorna mais nomes, só puuid."""
        url = f"https://{self.region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
        return self._get(url)

    def match_ids_by_puuid(
        self, puuid: str, queue: int = 420, count: int = 100, start: int = 0
    ) -> list[str]:
        url = f"https://{self.region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        return self._get(url, params={"queue": queue, "count": count, "start": start})

    def match(self, match_id: str) -> dict:
        url = f"https://{self.region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        return self._get(url)

    def timeline(self, match_id: str) -> dict:
        url = f"https://{self.region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
        return self._get(url)
