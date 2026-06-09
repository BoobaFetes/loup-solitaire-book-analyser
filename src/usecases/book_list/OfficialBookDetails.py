import base64
import logging
from datetime import date
from typing import cast

from bs4 import BeautifulSoup, Tag

from domain import BookPrice
from ports import HttpClientBase


class OfficialBookDetails:
    """Use cases for retrieve details of an official books"""

    def __init__(self, soup: BeautifulSoup):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._soup = soup

    def authors(self) -> list[str]:
        elements = self._soup.select("div.Book-contributors > p:first-child > a")
        if not elements:
            self._logger.error("No potential author information found in the page.")
            return []

        results: list[str] = []
        for author in [element.get_text(strip=False) for element in elements]:
            parts = [part.strip() if part else "" for part in author.split("\n")]
            results.append(" ".join(parts))

        return results

    def last_parution_date(self, default_value: str) -> str:
        element = self._soup.select_one("li.Book-detailsSet > p:nth-child(3) > strong")
        if not element:
            self._logger.error("No potential publication date found in the page.")
            return default_value

        _date = date.strptime(element.get_text(strip=True), "%d/%m/%Y")
        result = _date.isoformat()
        return result

    def numero(self, options: dict[str, int]) -> int:
        # arrange
        result: int = 0
        potential_numbers: list[Tag | None] = [
            self._soup.select_one("p.Book-suptitle"),
            self._soup.select_one("li.Book-detailsSet:nth-child(4) a"),
            self._soup.select_one("li.Book-detailsSet:nth-child(3) a"),
        ]
        number_unwanted_prefixes = [
            "loup solitaire - nouvelle présentation n°",
            "loup solitaire - ",
        ]
        # action
        available_texts = [
            num.get_text(strip=True) for num in potential_numbers if num is not None
        ]
        if available_texts:
            for num in available_texts:
                for unwanted_prefix in number_unwanted_prefixes:
                    if num.lower().startswith(unwanted_prefix):
                        numero = num[len(unwanted_prefix) :]
                        result = int(numero)
                        break
                if result:
                    break

        if result > 0:
            return result
        else:
            options["id"] -= 1
            return options["id"]

    def title(self, default_value: str) -> str:
        element = self._soup.select_one("h1.Book-title")
        return element.get_text(strip=True) if element else default_value

    def isbn(self, default_value: str) -> str:
        element = self._soup.select_one("li.Book-detailsSet > p:nth-child(2) > strong")
        return element.get_text(strip=True) if element else default_value

    def description(self, default_value: str) -> str:
        element = self._soup.select_one("div.Book-resume")
        return element.get_text(strip=True) if element else default_value

    async def image_url(self, client: HttpClientBase, default_value: str = "") -> str:
        element = self._soup.select_one("div.Book-cover img:first-child")
        if not element:
            self._logger.error("No potential image information found in the page.")
            return default_value

        url = (
            cast(str, element.attrs["src"])
            if element.attrs.get("src", "")
            else default_value
        )
        if not url:
            return default_value

        try:
            image_bytes = await client.get_content(url)
            image = base64.b64encode(image_bytes).decode("utf-8")
            return image
        except Exception as e:
            self._logger.warning(
                f"Failed to fetch or encode image from {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return default_value

    def prices(
        self, url: str, isbn: str, default_value: list[BookPrice] = []
    ) -> list[BookPrice]:
        element = self._soup.select_one("p.Book-price > span:last-child")
        if not element:
            self._logger.error("No potential price information found in the page.")
            return default_value

        gallimard_price: list[str] = element.get_text(strip=True).split()
        return (
            [
                BookPrice(
                    isbn=isbn,
                    source="Gallimard Jeunesse",
                    price=float(gallimard_price[0]),
                    currency=gallimard_price[1] if gallimard_price[1] == "€" else "",
                    url=url,
                )
            ]
            if gallimard_price
            else []
        )
