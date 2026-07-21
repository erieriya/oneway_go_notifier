import json

from src.models import Listing
from src.state import listings_to_state_dict, load_state, save_state


def make_listing():
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
    )


def test_load_state_missing_file_returns_default(tmp_path):
    state = load_state(tmp_path / "does_not_exist.json")
    assert state == {"initialized": False, "listings": {}}


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "state.json"
    listing = make_listing()
    state = {"initialized": True, "listings": listings_to_state_dict([listing])}

    save_state(state, path)
    loaded = load_state(path)

    assert loaded["initialized"] is True
    assert listing.id in loaded["listings"]
    assert loaded["listings"][listing.id]["start_shop"] == "トヨタレンタリース東京"


def test_save_state_writes_valid_json(tmp_path):
    path = tmp_path / "nested" / "state.json"
    save_state({"initialized": False, "listings": {}}, path)
    assert json.loads(path.read_text(encoding="utf-8"))["initialized"] is False
