"""Lifecycle history for every listing observed, independent of state.json
(which only reflects "now"). Used to build a track record of what actually
gets listed (routes, dates, how long they last) for planning real bookings.

Tracks, per listing id: when it was first seen, when it was last seen still
live, and when it disappeared (ended_at), plus the listing's own details
(shops, car, date range) as of when it was first recorded.
"""
from __future__ import annotations

import json
from pathlib import Path

from .models import Listing

DEFAULT_HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "route_history.json"


def load_history(path: Path = DEFAULT_HISTORY_PATH) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history: dict, path: Path = DEFAULT_HISTORY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2, sort_keys=True)


def update_history(
    history: dict,
    current_by_id: dict[str, Listing],
    matched_target_names: dict[str, list[str]],
    run_timestamp: str,
) -> dict:
    """Update history in place (also returned) for this run's observations.

    matched_target_names maps listing id -> list of route-filter target
    names it currently matches (may be an empty list if it matches none;
    callers that want every observed listing recorded should include all
    current listing ids as keys, regardless of whether any filter matches).
    """
    for listing_id, target_names in matched_target_names.items():
        listing = current_by_id[listing_id]
        record = history.get(listing_id)
        if record is None:
            history[listing_id] = {
                "start_shop": listing.start_shop,
                "start_area": listing.start_area,
                "return_shop": listing.return_shop,
                "return_area": listing.return_area,
                "car_name": listing.car_name,
                "car_plate": listing.car_plate,
                "condition": listing.condition,
                "date_range": listing.date_range,
                "matched_targets": sorted(target_names),
                "first_seen": run_timestamp,
                "last_seen": run_timestamp,
                "last_accepting": listing.accepting,
                "ended_at": None,
            }
        else:
            record["last_seen"] = run_timestamp
            record["last_accepting"] = listing.accepting
            record["ended_at"] = None
            record["matched_targets"] = sorted(set(record["matched_targets"]) | set(target_names))

    for listing_id, record in history.items():
        if record["ended_at"] is None and listing_id not in matched_target_names:
            record["ended_at"] = run_timestamp

    return history
