"""Data model for a single 片道GO! listing."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Listing:
    start_shop: str
    start_area: str
    return_shop: str
    return_area: str
    date_range: str
    car_name: str
    car_plate: str
    condition: str
    reserve_shop: str
    reserve_tel: str
    accepting: bool = True

    @property
    def id(self) -> str:
        key = "|".join(
            [self.start_shop, self.return_shop, self.car_name, self.car_plate, self.date_range]
        )
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = self.id
        return d

    @staticmethod
    def from_dict(d: dict) -> "Listing":
        return Listing(
            start_shop=d["start_shop"],
            start_area=d["start_area"],
            return_shop=d["return_shop"],
            return_area=d["return_area"],
            date_range=d["date_range"],
            car_name=d["car_name"],
            car_plate=d["car_plate"],
            condition=d["condition"],
            reserve_shop=d["reserve_shop"],
            reserve_tel=d["reserve_tel"],
            accepting=d.get("accepting", True),
        )
