import logging
from datetime import date
from typing import cast

from bs4 import BeautifulSoup, Tag

from domain import BookPrice
from ports.http import HttpClientBase
from ports.usecase import BookDetailsFinderBase


class GallimardBookDetailsFinder(BookDetailsFinderBase):
    def __init__(self, html: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__soup = BeautifulSoup(html, "html.parser")

    def isbn(self, default: str) -> str:
        element = self.__soup.select_one("li.Book-detailsSet > p:nth-child(2) > strong")
        return element.get_text(strip=True) if element else default

    def numero(self) -> int:
        # arrange
        result: int = 0
        potential_numbers: list[Tag | None] = [
            self.__soup.select_one("p.Book-suptitle"),
            self.__soup.select_one("li.Book-detailsSet:nth-child(4) a"),
            self.__soup.select_one("li.Book-detailsSet:nth-child(3) a"),
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

        return result if result > 0 else self._get_invalid_numero()

    def title(self, default: str) -> str:
        element = self.__soup.select_one("h1.Book-title")
        return element.get_text(strip=True) if element else default

    def authors(self) -> list[str]:
        elements = self.__soup.select("div.Book-contributors > p:first-child > a")
        if not elements:
            self.__logger.error("No potential author information found in the page.")
            return []

        results: list[str] = []
        for author in [element.get_text(strip=False) for element in elements]:
            parts = [part.strip() if part else "" for part in author.split("\n")]
            results.append(" ".join(parts))

        return results

    def lastParutionDate(self, default: str) -> str:
        element = self.__soup.select_one("li.Book-detailsSet > p:nth-child(3) > strong")
        if not element:
            self.__logger.error("No potential publication date found in the page.")
            return default

        _date = date.strptime(element.get_text(strip=True), "%d/%m/%Y")
        result = _date.isoformat()
        return result

    def description(self, default: str) -> str:
        element = self.__soup.select_one("div.Book-resume")
        return element.get_text(strip=True) if element else default

    def official(self) -> bool:
        return True

    def prices(self, **kwargs) -> list[BookPrice]:
        # check parameters
        isbn = kwargs.get("isbn", "")
        if not isbn:
            raise ValueError(
                "'isbn' property of type 'str' must be provided in kwargs for price extraction."
            )
        elif not isinstance(isbn, str):
            raise ValueError("'isbn' is not of type 'str' for price extraction.")

        url = kwargs.get("url", "")
        if not url:
            raise ValueError(
                "'url' property of type 'str' must be provided in kwargs for price extraction."
            )
        elif not isinstance(url, str):
            raise ValueError("'url' is not of type 'str' for price extraction.")

        # action
        element = self.__soup.select_one("p.Book-price > span:last-child")
        if not element:
            self.__logger.error("No potential price information found in the page.")
            return []

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

    async def image(self, client: HttpClientBase, **kwargs) -> str:
        element = self.__soup.select_one("div.Book-cover img:first-child")
        if not element:
            self.__logger.error("No potential image information found in the page.")
            return ""

        url = cast(str, element.attrs["src"]) if element.attrs.get("src", "") else ""
        if not url:
            return ""

        try:
            return await self._fetch_image(client, url)
        except Exception as e:
            self.__logger.warning(
                f"Failed to fetch or encode image from {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )
            return ""

    def is_classic_version(self) -> bool:
        raise NotImplementedError(
            "The method 'is_classic_version' is used in Gallimard Jeunesse web site."
        )
