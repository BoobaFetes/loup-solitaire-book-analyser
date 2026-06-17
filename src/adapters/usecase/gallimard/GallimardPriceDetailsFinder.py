import logging
import re
from collections.abc import Callable

from bs4 import BeautifulSoup, Tag

from ports.usecase import PriceDetailsFinderBase


class GallimardPriceDetailsFinder(PriceDetailsFinderBase):
    def __init__(self, html: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__soup = BeautifulSoup(html, "html.parser")

    def url(self, **kwargs) -> str:
        raise NotImplementedError(
            "The 'url' method is not used for GallimardPriceDetailsFinder as url is already obtained when book is fetched."
        )

    def price_and_currency(self, **kwargs) -> tuple[float, str]:
        element = self.__soup.select_one("p.Book-price > span:last-child")
        if not element:
            self.__logger.error("No potential price information found in the page.")
            return 0.0, "not set"

        price, currency = element.get_text(strip=True).split()

        return (
            float(price.replace(",", ".")),
            currency if currency == "€" else "",
        )

        price, currency = element.get_text(strip=True).split()
        return float(price.replace(",", ".")), currency

    def __is_matching_title_fn(
        self, title_pattern: re.Pattern[str], isbn: str
    ) -> Callable[[Tag], bool]:
        def is_matching_item(parent: Tag) -> bool:
            title_element = parent.select_one('div[data-cy="title-recipe"] h2')
            if not title_element:
                return False
            return bool(title_pattern.search(title_element.get_text(strip=True)))

        return is_matching_item
