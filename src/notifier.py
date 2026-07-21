"""Sends new-listing notifications to a Discord webhook."""
from __future__ import annotations

import requests

from .models import Listing

SOURCE_URL = "https://cp.toyota.jp/rentacar/"
TIMEOUT = 15


def _build_embed(listing: Listing, available_count: int | None, has_filter: bool) -> dict:
    car = listing.car_name + (f"　{listing.car_plate}" if listing.car_plate else "")
    status = "🟢 受付中" if listing.accepting else "🔴 受付終了"
    fields = [
        {"name": "出発店舗", "value": f"{listing.start_shop}（{listing.start_area}）", "inline": False},
        {"name": "返却店舗", "value": f"{listing.return_shop}（{listing.return_area}）", "inline": False},
        {"name": "車種", "value": car or "不明", "inline": True},
        {"name": "車両条件", "value": listing.condition or "-", "inline": True},
        {"name": "出発期間", "value": listing.date_range or "-", "inline": False},
        {"name": "受付状況", "value": status, "inline": True},
        {
            "name": "予約電話番号",
            "value": f"{listing.reserve_shop} {listing.reserve_tel}".strip(),
            "inline": False,
        },
    ]
    if available_count is not None:
        label = "現在の受付中台数（この条件に一致）" if has_filter else "現在の受付中台数（全体）"
        fields.append({"name": label, "value": f"{available_count}台", "inline": False})
    return {
        "title": "🚗 片道GO! 新着掲載",
        "url": SOURCE_URL,
        "color": 0xE60012 if listing.accepting else 0x808080,
        "fields": fields,
    }


def send_new_listing(
    webhook_url: str,
    listing: Listing,
    thread_id: str | None = None,
    available_count: int | None = None,
    has_filter: bool = False,
) -> None:
    payload = {"embeds": [_build_embed(listing, available_count, has_filter)]}
    params = {"thread_id": thread_id} if thread_id else None
    response = requests.post(webhook_url, json=payload, params=params, timeout=TIMEOUT)
    response.raise_for_status()
