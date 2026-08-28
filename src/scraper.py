"""HTTP fetch layer for the 片道GO! campaign page.

Kept separate from parsing so that a change in transport (e.g. adding
retries, switching to Playwright) never touches the HTML parsing logic.
"""
from __future__ import annotations

import time

import requests

URL = "https://cp.toyota.jp/rentacar/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 20
RETRIES = 3
BACKOFF_SECONDS = 5.0


def fetch_html(url: str = URL, retries: int = RETRIES, backoff_seconds: float = BACKOFF_SECONDS) -> str:
    last_exc: requests.RequestException | None = None
    for attempt in range(retries):
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(backoff_seconds * (attempt + 1))
    raise last_exc
