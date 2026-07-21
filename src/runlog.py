"""Appends one line per run to data/run_log.jsonl.

Unlike state.json (which only holds the latest snapshot), this keeps a
history so "it ran but nothing changed" is visible without digging through
GitHub Actions' own log retention. Trimmed to the last N entries so the file
doesn't grow unbounded in the git history.
"""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "run_log.jsonl"
DEFAULT_MAX_ENTRIES = 2000


def append_entry(
    entry: dict,
    path: Path = DEFAULT_LOG_PATH,
    max_entries: int = DEFAULT_MAX_ENTRIES,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    lines.append(json.dumps(entry, ensure_ascii=False))
    if max_entries > 0:
        lines = lines[-max_entries:]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
