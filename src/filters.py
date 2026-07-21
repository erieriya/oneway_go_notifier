"""Route filtering shared by ROUTE_FILTERS and per-thread NOTIFY_TARGETS.

Format: comma-separated "start:return" rules, matched as substrings against
the shop/area names. Each side may list multiple alternatives separated by
"|" (OR), which lets a rule express a region made of several operator names
or prefectures, e.g. a "関東発・関西着" rule:

    レンタリース東京|レンタリース神奈川|モビリティサービス:レンタリース大阪|レンタリース京都

Empty/unset input means "no filtering" (everything matches).
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import Listing


@dataclass(frozen=True)
class RoutePair:
    start_alternatives: tuple[str, ...]
    return_alternatives: tuple[str, ...]


def _split_alternatives(side: str) -> tuple[str, ...]:
    return tuple(s.strip() for s in side.split("|") if s.strip())


def parse_filters(raw: str | None) -> list[RoutePair]:
    if not raw or not raw.strip():
        return []
    pairs: list[RoutePair] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        start_side, _, return_side = chunk.partition(":")
        start_alts = _split_alternatives(start_side)
        return_alts = _split_alternatives(return_side)
        if start_alts and return_alts:
            pairs.append(RoutePair(start_alts, return_alts))
    return pairs


def matches(listing: Listing, filters: list[RoutePair]) -> bool:
    if not filters:
        return True
    start_haystack = listing.start_shop + listing.start_area
    return_haystack = listing.return_shop + listing.return_area
    return any(
        any(alt in start_haystack for alt in rule.start_alternatives)
        and any(alt in return_haystack for alt in rule.return_alternatives)
        for rule in filters
    )
