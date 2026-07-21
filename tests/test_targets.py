import json

from src.filters import matches
from src.models import Listing
from src.targets import parse_targets


def make_listing(start_shop, return_shop):
    return Listing(
        start_shop=start_shop,
        start_area="",
        return_shop=return_shop,
        return_area="",
        date_range="2026年7月15日 ～ 7月21日",
        car_name="ヤリス",
        car_plate="品川500あ1234",
        condition="禁煙",
        reserve_shop="新宿店",
        reserve_tel="03-0000-0000",
    )


def test_no_targets_configured_falls_back_to_single_default_target():
    targets = parse_targets(None, fallback_thread_id="123", fallback_filters_raw=None)
    assert len(targets) == 1
    assert targets[0].thread_id == "123"
    assert targets[0].filters == []


def test_notify_targets_json_defines_multiple_threads_with_own_filters():
    raw = json.dumps(
        [
            {"name": "関東→関西", "thread_id": "111", "filters": "レンタリース東京:レンタリース大阪"},
            {"name": "関西→関東", "thread_id": "222", "filters": "レンタリース大阪:レンタリース東京"},
        ]
    )
    targets = parse_targets(raw)
    assert len(targets) == 2

    kanto_to_kansai = make_listing("トヨタレンタリース東京", "トヨタレンタリース大阪")
    kansai_to_kanto = make_listing("トヨタレンタリース大阪", "トヨタレンタリース東京")

    kanto_target = next(t for t in targets if t.name == "関東→関西")
    kansai_target = next(t for t in targets if t.name == "関西→関東")

    assert matches(kanto_to_kansai, kanto_target.filters) is True
    assert matches(kanto_to_kansai, kansai_target.filters) is False
    assert matches(kansai_to_kanto, kansai_target.filters) is True
    assert matches(kansai_to_kanto, kanto_target.filters) is False


def test_target_without_explicit_name_defaults_to_thread_id():
    targets = parse_targets(json.dumps([{"thread_id": "999"}]))
    assert targets[0].name == "999"
