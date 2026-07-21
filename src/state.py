"""Load/save previously-seen listing state."""
from __future__ import annotations

import json
from pathlib import Path

from .models import Listing

DEFAULT_STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "state.json"


def load_state(path: Path = DEFAULT_STATE_PATH) -> dict:
    if not path.exists():
        return {"initialized": False, "listings": {}}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict, path: Path = DEFAULT_STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)


def listings_to_state_dict(listings: list[Listing]) -> dict:
    return {listing.id: listing.to_dict() for listing in listings}
