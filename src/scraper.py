"""HTTP fetch layer for the 片道GO! campaign page.

Kept separate from parsing so that a change in transport (e.g. adding
retries, switching to Playwright) never touches the HTML parsing logic.
"""
from __future__ import annotations

import requests

URL = "https://cp.toyota.jp/rentacar/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 20


def fetch_html(url: str = URL) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text
