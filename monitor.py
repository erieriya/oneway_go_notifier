"""Entry point: fetch 片道GO! listings, diff against saved state, notify Discord."""
from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime, timezone

from src.filters import matches
from src.history import load_history, save_history, update_history
from src.notifier import send_new_listing
from src.parser import parse_listings
from src.runlog import NOTIFY_FAILURES_PATH, append_entry
from src.scraper import fetch_html
from src.state import listings_to_state_dict, load_state, save_state
from src.targets import parse_targets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("monitor")


def main() -> int:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    targets = parse_targets(
        os.environ.get("NOTIFY_TARGETS"),
        fallback_thread_id=os.environ.get("DISCORD_THREAD_ID") or None,
        fallback_filters_raw=os.environ.get("ROUTE_FILTERS"),
    )

    run_started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.monotonic()
    try:
        html = fetch_html()
        current_listings = parse_listings(html)
    except Exception as exc:
        logger.exception("取得または解析に失敗しました")
        append_entry(
            {
                "timestamp": run_started_at,
                "elapsed_seconds": round(time.monotonic() - start_time, 2),
                "fetched_count": None,
                "new_count": None,
                "notified": 0,
                "notify_errors": 0,
                "error": str(exc),
            }
        )
        return 1
    elapsed = time.monotonic() - start_time

    current_by_id = {listing.id: listing for listing in current_listings}
    state = load_state()
    previous_ids = set(state.get("listings", {}).keys())
    is_first_run = not state.get("initialized", False)

    new_ids = [] if is_first_run else [i for i in current_by_id if i not in previous_ids]
    notifiable_ids = [i for i in new_ids if current_by_id[i].accepting]
    skipped_not_accepting = len(new_ids) - len(notifiable_ids)
    notified = 0
    notify_errors = 0

    if notifiable_ids and not webhook_url:
        logger.warning("DISCORD_WEBHOOK_URL 未設定のため通知をスキップ")

    if notifiable_ids and webhook_url:
        target_available_counts = [
            sum(
                1
                for listing in current_listings
                if listing.accepting and matches(listing, target.filters)
            )
            for target in targets
        ]
        for listing_id in notifiable_ids:
            listing = current_by_id[listing_id]
            for target, available_count in zip(targets, target_available_counts):
                if not matches(listing, target.filters):
                    continue
                try:
                    send_new_listing(
                        webhook_url,
                        listing,
                        thread_id=target.thread_id,
                        available_count=available_count,
                        has_filter=bool(target.filters),
                    )
                    notified += 1
                except Exception as exc:
                    logger.exception(
                        "Discord通知に失敗しました: listing=%s target=%s", listing_id, target.name
                    )
                    notify_errors += 1
                    append_entry(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "listing_id": listing_id,
                            "target": target.name,
                            "thread_id": target.thread_id,
                            "start_shop": listing.start_shop,
                            "return_shop": listing.return_shop,
                            "car_name": listing.car_name,
                            "date_range": listing.date_range,
                            "error": str(exc),
                        },
                        path=NOTIFY_FAILURES_PATH,
                    )

    state["initialized"] = True
    state["listings"] = listings_to_state_dict(current_listings)
    save_state(state)

    # Every currently observed listing gets a history record (not just ones
    # matching a route filter) so past listings can inform booking strategy
    # later. matched_targets is still recorded as useful metadata.
    filtered_targets = [t for t in targets if t.filters]
    history_matches = {
        listing_id: [t.name for t in filtered_targets if matches(listing, t.filters)]
        for listing_id, listing in current_by_id.items()
    }
    history = load_history()
    update_history(history, current_by_id, history_matches, run_started_at)
    save_history(history)

    append_entry(
        {
            "timestamp": run_started_at,
            "elapsed_seconds": round(elapsed, 2),
            "fetched_count": len(current_listings),
            "new_count": len(new_ids),
            "skipped_not_accepting": skipped_not_accepting,
            "notified": notified,
            "notify_errors": notify_errors,
            "first_run": is_first_run,
            "error": None,
        }
    )

    logger.info(
        "取得件数=%d 新規件数=%d 受付終了で通知スキップ=%d 通知件数=%d 通知失敗=%d 取得時間=%.2fs 初回実行=%s",
        len(current_listings),
        len(new_ids),
        skipped_not_accepting,
        notified,
        notify_errors,
        elapsed,
        is_first_run,
    )
    return 1 if notify_errors else 0


if __name__ == "__main__":
    sys.exit(main())
