import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


class AmazonPriceSourceDetails:
    def __init__(self, html: str):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._soup = BeautifulSoup(html, "html.parser")

    def url(self, base_url: str, isbn: str) -> str:
        element = self._soup.select_one(
            f'div[role="listitem"] div[data-cy="title-recipe"] > a[href*="keywords={isbn}"]'
        )
        if not element or not isinstance(element, Tag) or element.name != "a":
            self._logger.error(
                "No potential url to the details page found in the page."
            )
            return ""

        segment = str(element.attrs.get("href", "")).strip()
        if not segment:
            self._logger.error("The link to the details page is empty.")
            return ""

        return urljoin(base_url, segment)

    def price_and_currency(self, isbn: str) -> tuple[float, str]:
        element = self._soup.select_one(
            'div[role="listitem"] div[data-cy="price-recipe"] span.a-price > span:first-child'
        )
        if not element:
            self._logger.error("No potential price information found in the page.")
            return 0.0, "not set"

        price, currency = element.get_text(strip=True).split()
        return float(price.replace(",", ".")), currency
