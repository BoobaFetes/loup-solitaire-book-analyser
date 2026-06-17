import logging
import re
from collections.abc import Callable
from typing import cast
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from ports.usecase import PriceDetailsFinderBase


class AmazonPriceDetailsFinder(PriceDetailsFinderBase):
    def __init__(self, html: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__soup = BeautifulSoup(html, "html.parser")

    def url(self, **kwargs) -> str:
        # check parameters
        isbn = kwargs.get("isbn", "")
        if not isbn:
            raise ValueError(
                "'isbn' property of type 'str' must be provided in kwargs for URL extraction."
            )
        elif not isinstance(isbn, str):
            raise ValueError("'isbn' is not of type 'str' for URL extraction.")
        base_url = kwargs.get("base_url", "")
        if not base_url:
            raise ValueError(
                "'base_url' property of type 'str' must be provided in kwargs for URL extraction."
            )
        elif not isinstance(base_url, str):
            raise ValueError("'base_url' is not of type 'str' for URL extraction.")

        # action
        element = self.__soup.select_one(
            f'div[role="listitem"] div[data-cy="title-recipe"] > a[href*="keywords={isbn}"]'
        )
        if not element or not isinstance(element, Tag) or element.name != "a":
            self.__logger.error(
                f"No potential url to the details page found in the page for isbn {isbn}."
            )
            return ""

        segment = str(element.attrs.get("href", "")).strip()
        if not segment:
            self.__logger.error(
                f"The link to the details page is empty for isbn {isbn}."
            )
            return ""

        return urljoin(base_url, segment)

    def price_and_currency(self, **kwargs) -> tuple[float, str]:
        # check parameters
        isbn = kwargs.get("isbn", "")
        if not isbn:
            raise ValueError(
                "'isbn' property of type 'str' must be provided in kwargs for price and currency extraction."
            )
        elif not isinstance(isbn, str):
            raise ValueError(
                "'isbn' is not of type 'str' for price and currency extraction."
            )

        title_pattern = cast(re.Pattern[str], kwargs.get("title_pattern", None))
        if not title_pattern:
            raise ValueError(
                "'title_pattern' property of type 're.Pattern' must be provided in kwargs for price and currency extraction."
            )
        elif not isinstance(title_pattern, re.Pattern):
            raise ValueError(
                "'title_pattern' is not of type 're.Pattern' for price and currency extraction."
            )

        # actions

        # select the first element that match the name of the book
        items = list(
            filter(
                self.__is_matching_title_fn(title_pattern, isbn),
                self.__soup.select('div[role="listitem"]'),
            )
        )
        if not items:
            self.__logger.error(
                f"No item found with matching title in the page for isbn {isbn}."
            )
            return 0.0, "not set"

        element = items[0].select_one(
            'div[data-cy="price-recipe"] span.a-price > span:first-child',
        )
        if not element:
            self.__logger.error(
                f"No potential price information found in the page for isbn {isbn}."
            )
            return 0.0, "not set"

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
