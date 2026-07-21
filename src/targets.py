"""Notification targets: each pairs a Discord thread with its own route filter.

Configured via the NOTIFY_TARGETS env var as a JSON array, e.g. to split
"関東発・関西着" and "関西発・関東着" into two threads:

    [
      {"name": "関東→関西", "thread_id": "1111111111111111",
       "filters": "レンタリース東京|レンタリース神奈川|レンタリース埼玉|レンタリース千葉:レンタリース大阪|レンタリース京都|レンタリース兵庫"},
      {"name": "関西→関東", "thread_id": "2222222222222222",
       "filters": "レンタリース大阪|レンタリース京都|レンタリース兵庫:レンタリース東京|レンタリース神奈川|レンタリース埼玉|レンタリース千葉"}
    ]

A listing may match more than one target and will be posted to each. If
NOTIFY_TARGETS is unset, a single target is built from DISCORD_THREAD_ID and
ROUTE_FILTERS so the simple single-thread setup keeps working unchanged.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from .filters import RoutePair, parse_filters


@dataclass(frozen=True)
class NotifyTarget:
    name: str
    thread_id: str | None
    filters: list[RoutePair]


def parse_targets(
    raw_json: str | None,
    fallback_thread_id: str | None = None,
    fallback_filters_raw: str | None = None,
) -> list[NotifyTarget]:
    if raw_json and raw_json.strip():
        entries = json.loads(raw_json)
        return [
            NotifyTarget(
                name=entry.get("name") or entry.get("thread_id") or "default",
                thread_id=(entry.get("thread_id") or None),
                filters=parse_filters(entry.get("filters")),
            )
            for entry in entries
        ]
    return [
        NotifyTarget(
            name="default",
            thread_id=fallback_thread_id,
            filters=parse_filters(fallback_filters_raw),
        )
    ]
