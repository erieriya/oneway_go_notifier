from src.models import Listing
from src.notifier import _build_embed


def make_listing(accepting=True):
    return Listing(
        start_shop="トヨタレンタリース東京",
        start_area="東京都",
        return_shop="トヨタレンタリース新大阪",
        return_area="大阪府",
        date_range="2026年7月15日 ～ 7月21日",
        car_name="ヤリス",
        car_plate="品川500あ1234",
        condition="禁煙",
        reserve_shop="新宿店",
        reserve_tel="03-0000-0000",
        accepting=accepting,
    )


def test_embed_omits_available_count_field_when_none():
    embed = _build_embed(make_listing(), available_count=None, has_filter=False)
    names = [f["name"] for f in embed["fields"]]
    assert not any("受付中台数" in n for n in names)


def test_embed_shows_overall_count_when_no_filter():
    embed = _build_embed(make_listing(), available_count=42, has_filter=False)
    field = next(f for f in embed["fields"] if "受付中台数" in f["name"])
    assert field["name"] == "現在の受付中台数（全体）"
    assert field["value"] == "42台"


def test_embed_shows_condition_matched_count_when_filtered():
    embed = _build_embed(make_listing(), available_count=7, has_filter=True)
    field = next(f for f in embed["fields"] if "受付中台数" in f["name"])
    assert field["name"] == "現在の受付中台数（この条件に一致）"
    assert field["value"] == "7台"


def test_embed_shows_accepting_status():
    embed = _build_embed(make_listing(accepting=True), available_count=None, has_filter=False)
    status_field = next(f for f in embed["fields"] if f["name"] == "受付状況")
    assert status_field["value"] == "🟢 受付中"
    assert embed["color"] == 0xE60012


def test_embed_shows_closed_status():
    embed = _build_embed(make_listing(accepting=False), available_count=None, has_filter=False)
    status_field = next(f for f in embed["fields"] if f["name"] == "受付状況")
    assert status_field["value"] == "🔴 受付終了"
    assert embed["color"] == 0x808080
