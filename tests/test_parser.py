from pathlib import Path

from src.parser import parse_listings

FIXTURE = Path(__file__).parent / "fixtures" / "sample.html"


def test_parse_listings_extracts_all_fields():
    html = FIXTURE.read_text(encoding="utf-8")
    listings = parse_listings(html)

    assert len(listings) == 3

    first = listings[0]
    assert first.start_shop == "トヨタレンタリース宮城 気仙沼店"
    assert first.start_area == "宮城県 気仙沼市"
    assert first.return_shop == "トヨタレンタリース青森 返却可能店舗"
    assert first.return_area == "下記参照"
    assert first.date_range == "2026年7月15日 ～ 7月21日"
    assert first.car_name == "ヤリス"
    assert first.car_plate == "八戸500わ9187"
    assert first.condition == "5人乗・禁煙車"
    assert first.reserve_shop == "気仙沼店"
    assert first.reserve_tel == "0226-22-0100"
    assert first.accepting is False  # has the show-entry-end (受付終了) class

    second = listings[1]
    assert second.car_name == "アルファード"
    assert second.car_plate == "郡山300わ1107"
    assert second.accepting is False

    third = listings[2]
    assert third.car_name == "カローラツーリングHV"
    assert third.accepting is True  # no show-entry-end class -> still accepting


def test_listing_ids_are_stable_and_unique():
    listings = parse_listings(FIXTURE.read_text(encoding="utf-8"))
    ids = [listing.id for listing in listings]

    assert len(ids) == len(set(ids))
    assert listings[0].id == parse_listings(FIXTURE.read_text(encoding="utf-8"))[0].id


def test_parse_listings_empty_when_container_missing():
    assert parse_listings("<html><body>no data</body></html>") == []
