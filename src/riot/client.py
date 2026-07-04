"""Cliente da Riot Games API com rate limiting e retry.

Limites da chave de desenvolvimento: 20 req/1s e 100 req/120s.
O cliente usa janela deslizante e respeita o header Retry-After em 429.
"""
import time
from collections import deque

import requests

from src.config import RIOT_API_KEY, RIOT_PLATFORM, RIOT_REGION


class RiotClient:
    def __init__(self, requests_per_2min: int = 95):
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": RIOT_API_KEY})
        self.limit = requests_per_2min
        self.window: deque[float] = deque()

    # ---------------- rate limiting ----------------
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

    # ---------------- endpoints ----------------
    def challenger_league(self, queue: str = "RANKED_SOLO_5x5") -> dict:
        url = (
            f"https://{RIOT_PLATFORM}.api.riotgames.com"
            f"/lol/league/v4/challengerleagues/by-queue/{queue}"
        )
        return self._get(url)

    def grandmaster_league(self, queue: str = "RANKED_SOLO_5x5") -> dict:
        url = (
            f"https://{RIOT_PLATFORM}.api.riotgames.com"
            f"/lol/league/v4/grandmasterleagues/by-queue/{queue}"
        )
        return self._get(url)

    def account_by_puuid(self, puuid: str) -> dict:
        """gameName/tagLine de um jogador (account-v1) — o endpoint de
        liga não retorna mais nomes, só puuid."""
        url = (
            f"https://{RIOT_REGION}.api.riotgames.com"
            f"/riot/account/v1/accounts/by-puuid/{puuid}"
        )
        return self._get(url)

    def match_ids_by_puuid(
        self, puuid: str, queue: int = 420, count: int = 100, start: int = 0
    ) -> list[str]:
        url = (
            f"https://{RIOT_REGION}.api.riotgames.com"
            f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        )
        return self._get(url, params={"queue": queue, "count": count, "start": start})

    def match(self, match_id: str) -> dict:
        url = f"https://{RIOT_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        return self._get(url)

    def timeline(self, match_id: str) -> dict:
        url = (
            f"https://{RIOT_REGION}.api.riotgames.com"
            f"/lol/match/v5/matches/{match_id}/timeline"
        )
        return self._get(url)
