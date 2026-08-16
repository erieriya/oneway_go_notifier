from src.history import update_history
from src.models import Listing


def make_listing(start_shop="トヨタレンタリース東京", return_shop="トヨタレンタリース大阪", accepting=True):
    return Listing(
        start_shop=start_shop,
        start_area="東京都",
        return_shop=return_shop,
        return_area="大阪府",
        date_range="2026年7月15日 ～ 7月21日",
        car_name="ヤリス",
        car_plate="品川500あ1234",
        condition="禁煙",
        reserve_shop="新宿店",
        reserve_tel="03-0000-0000",
        accepting=accepting,
    )


def test_new_matching_listing_creates_record():
    listing = make_listing()
    current_by_id = {listing.id: listing}
    history = update_history({}, current_by_id, {listing.id: ["関東→関西"]}, "t1")

    record = history[listing.id]
    assert record["first_seen"] == "t1"
    assert record["last_seen"] == "t1"
    assert record["ended_at"] is None
    assert record["matched_targets"] == ["関東→関西"]
    assert record["date_range"] == "2026年7月15日 ～ 7月21日"


def test_still_present_updates_last_seen_but_not_first_seen():
    listing = make_listing()
    current_by_id = {listing.id: listing}
    history = update_history({}, current_by_id, {listing.id: ["関東→関西"]}, "t1")
    history = update_history(history, current_by_id, {listing.id: ["関東→関西"]}, "t2")

    record = history[listing.id]
    assert record["first_seen"] == "t1"
    assert record["last_seen"] == "t2"
    assert record["ended_at"] is None


def test_disappearing_listing_gets_ended_at():
    listing = make_listing()
    current_by_id = {listing.id: listing}
    history = update_history({}, current_by_id, {listing.id: ["関東→関西"]}, "t1")

    # next run: listing no longer present/matching at all
    history = update_history(history, {}, {}, "t2")

    record = history[listing.id]
    assert record["last_seen"] == "t1"
    assert record["ended_at"] == "t2"


def test_reappearing_listing_clears_ended_at():
    listing = make_listing()
    current_by_id = {listing.id: listing}
    history = update_history({}, current_by_id, {listing.id: ["関東→関西"]}, "t1")
    history = update_history(history, {}, {}, "t2")
    history = update_history(history, current_by_id, {listing.id: ["関東→関西"]}, "t3")

    record = history[listing.id]
    assert record["first_seen"] == "t1"
    assert record["last_seen"] == "t3"
    assert record["ended_at"] is None


def test_matched_targets_accumulate_across_runs():
    listing = make_listing()
    current_by_id = {listing.id: listing}
    history = update_history({}, current_by_id, {listing.id: ["関東→関西"]}, "t1")
    history = update_history(history, current_by_id, {listing.id: ["関西→関東"]}, "t2")

    assert set(history[listing.id]["matched_targets"]) == {"関東→関西", "関西→関東"}


def test_listing_with_no_matching_target_is_still_recorded():
    listing = make_listing(start_shop="トヨタレンタリース福岡", return_shop="トヨタレンタリース長崎")
    current_by_id = {listing.id: listing}
    history = update_history({}, current_by_id, {listing.id: []}, "t1")

    record = history[listing.id]
    assert record["first_seen"] == "t1"
    assert record["matched_targets"] == []


def test_last_accepting_reflects_latest_observation():
    listing = make_listing(accepting=True)
    current_by_id = {listing.id: listing}
    history = update_history({}, current_by_id, {listing.id: []}, "t1")
    assert history[listing.id]["last_accepting"] is True

    sold_out_listing = make_listing(accepting=False)
    current_by_id = {sold_out_listing.id: sold_out_listing}
    history = update_history(history, current_by_id, {sold_out_listing.id: []}, "t2")
    assert history[sold_out_listing.id]["last_accepting"] is False
