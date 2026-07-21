"""Parses 片道GO! listing HTML into Listing objects.

Isolated from scraper.py (transport) and state/notifier (downstream use) so
that a markup change on the site only requires editing this file.
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from .models import Listing

LIST_CONTAINER_ID = "service-items-shop-type-start"
NAME_SPLIT_RE = re.compile(r"[　\s]+")


def _text_no_label(container: Tag) -> str:
    p = container.select_one("p:not(.label-sp)")
    return p.get_text(strip=True) if p else ""


def _shop_name_and_area(shop_div: Tag) -> tuple[str, str]:
    p = shop_div.select_one("p:not(.label-sp)")
    if p is None:
        return "", ""
    small = p.find("small")
    area = small.get_text(strip=True).strip("（）") if small else ""
    name = p.contents[0].strip() if p.contents else ""
    return name, area


def _split_car_type(text: str) -> tuple[str, str]:
    parts = NAME_SPLIT_RE.split(text, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return text.strip(), ""


def parse_listings(html: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find(id=LIST_CONTAINER_ID)
    if container is None:
        return []

    listings: list[Listing] = []
    for item in container.select("li.service-item"):
        body_div = item.select_one(".service-item__body")
        shop_start = item.select_one(".service-item__shop-start")
        shop_return = item.select_one(".service-item__shop-return")
        date_div = item.select_one(".service-item__date")
        car_type_div = item.select_one(".service-item__info__car-type")
        condition_div = item.select_one(".service-item__info__condition")
        reserve_shop_div = item.select_one(".service-item__reserve-shop")
        reserve_tel_div = item.select_one(".service-item__reserve-tel")

        if not (shop_start and shop_return and date_div and car_type_div):
            continue

        start_shop, start_area = _shop_name_and_area(shop_start)
        return_shop, return_area = _shop_name_and_area(shop_return)
        car_name, car_plate = _split_car_type(_text_no_label(car_type_div))
        # The site overlays a CSS-generated "受付終了" badge via this class
        # (::before{content:'受付終了'}) rather than putting the text in the DOM.
        body_classes = body_div.get("class", []) if body_div else []
        accepting = "show-entry-end" not in body_classes

        listings.append(
            Listing(
                start_shop=start_shop,
                start_area=start_area,
                return_shop=return_shop,
                return_area=return_area,
                date_range=_text_no_label(date_div),
                car_name=car_name,
                car_plate=car_plate,
                condition=_text_no_label(condition_div) if condition_div else "",
                reserve_shop=reserve_shop_div.get_text(strip=True) if reserve_shop_div else "",
                reserve_tel=reserve_tel_div.get_text(strip=True) if reserve_tel_div else "",
                accepting=accepting,
            )
        )

    return listings
