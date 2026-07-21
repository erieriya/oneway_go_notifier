from src.filters import matches, parse_filters
from src.models import Listing


def make_listing(start_shop="トヨタレンタリース東京", return_shop="トヨタレンタリース新大阪"):
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
    )


def test_no_filters_means_everything_matches():
    assert matches(make_listing(), parse_filters(None)) is True
    assert matches(make_listing(), parse_filters("")) is True


def test_filter_matches_start_and_return_substrings():
    filters = parse_filters("東京:大阪")
    assert matches(make_listing(), filters) is True


def test_filter_rejects_non_matching_route():
    filters = parse_filters("大阪:東京")
    assert matches(make_listing(), filters) is False


def test_multiple_rules_are_ored():
    filters = parse_filters("大阪:東京,東京:大阪")
    assert matches(make_listing(), filters) is True


def test_or_alternatives_within_a_side_for_region_grouping():
    # "関東発・関西着" style rule: several operator names per side.
    filters = parse_filters(
        "レンタリース東京|レンタリース神奈川:レンタリース新大阪|レンタリース京都"
    )
    assert matches(make_listing(), filters) is True

    kanagawa_to_kyoto = make_listing(
        start_shop="トヨタレンタリース神奈川", return_shop="トヨタレンタリース京都"
    )
    assert matches(kanagawa_to_kyoto, filters) is True

    tohoku_to_osaka = make_listing(start_shop="トヨタレンタリース宮城")
    assert matches(tohoku_to_osaka, filters) is False
