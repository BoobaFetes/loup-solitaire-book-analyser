import asyncio
import base64
from typing import Literal, cast

from bs4 import BeautifulSoup, Tag

from domain import Book, BookPrice
from ports import HttpClientBase
from usecases.BookUseCasesInterface import BookUseCasesInterface


class OfficialBookUseCases(BookUseCasesInterface):
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        results: list[Book] = []

        active_client = client or self._client
        async with active_client as client_instance:
            urls = await self._fetch_book_urls(client_instance)

            self._logger.info(f"Fetching book details for {len(urls)} URLs")
            tasks = [self.fetch_book(url, client_instance) for url in urls]
            results = [book for book in await asyncio.gather(*tasks) if book]
        return results

    # region dependencies: fetch_books

    async def _fetch_book_urls(self, client: HttpClientBase):
        # arrange
        def _build_full_url(segment: str) -> str:
            return f"{self._url_base}{segment}"

        result: list[str] = []
        segment: str = r"/catalogue/fragment?page=1&text=loup%20solitaire"

        while segment:
            # fetch page content
            self._logger.info(f"Fetching list of books from '{segment}'")
            json = await client.get_json(_build_full_url(segment))

            # parse HTML content to find book detail links
            self._logger.info(
                f"Parsing HTML content from '{_build_full_url(segment)}' to find book details",
            )
            html = json.get("html", "")
            if html:
                soup = BeautifulSoup(html, "html.parser")
                anchors = soup.select("p.BookItem-title > a")

                result.extend(
                    [
                        _build_full_url(str(a["href"]))
                        for a in anchors
                        if a.has_attr("href")
                    ]
                )
            else:
                self._logger.warning(
                    f"No HTML content found at '{_build_full_url(segment)}'"
                )

            # check for next page URL
            next_url: str | Literal[False] = json.get("next-url", False)
            segment = next_url if next_url else ""
            if not segment:
                self._logger.info("no more pages to fetch")

        self._logger.info(f"Found {len(result)} book URLs")
        return result

    # endregion

    async def fetch_book(
        self, url: str, client: HttpClientBase | None = None
    ) -> Book | None:
        book: Book | None = None
        numero_options = {"id": 0}
        try:
            self._logger.info(
                f"get book details from URL: {url}",
            )
            active_client = client or self._client
            html = await active_client.get_text(url)
            soup = BeautifulSoup(html, "html.parser")

            if "Joe Dever" not in self._get_authors(soup):
                self._logger.warning(
                    f"Book at URL: {url} does not have Joe Dever as author. Skipping.",
                )
                return None

            id = numero = self._get_numero(soup, numero_options)
            if numero < 0:
                self._logger.warning(
                    f"Could not find a valid book's number at URL: {url}. Defaulting to {numero_options['id']}.",
                )

            book = Book(
                id=id,
                url=url,
                numero=numero,
                titre=self._get_title(soup, ""),
                description=self._get_description(soup, ""),
                isbn=self._get_isbn(soup, ""),
                image=await self._get_image_url(soup, active_client),
                prices=self._get_prices(soup, url, []),
                official=True,
            )
        except Exception as e:
            self._logger.error(
                f"Error while fetching book details for URL: {url} - reason: {e}",
            )

        return book

    # region dependencies: fetch_book

    def _get_authors(self, soup: BeautifulSoup) -> list[str]:
        elements = soup.select("div.Book-contributors > p > a")
        if not elements:
            return []

        result: list[str] = []
        for author in [element.get_text(strip=False) for element in elements]:
            parts = [part.strip() if part else "" for part in author.split("\n")]
            result.append(" ".join(parts))

        return result

    def _get_numero(self, soup: BeautifulSoup, options: dict[str, int]) -> int:
        # arrange
        result: int = 0
        potential_numbers: list[Tag | None] = [
            soup.select_one("p.Book-suptitle"),
            soup.select_one("li.Book-detailsSet:nth-child(4) a"),
            soup.select_one("li.Book-detailsSet:nth-child(3) a"),
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

    def _get_title(self, soup: BeautifulSoup, default_value: str) -> str:
        element = soup.select_one("h1.Book-title")
        return element.get_text(strip=True) if element else default_value

    def _get_isbn(self, soup: BeautifulSoup, default_value: str) -> str:
        element = soup.select_one("li.Book-detailsSet > p:nth-child(2) > strong")
        return element.get_text(strip=True) if element else default_value

    def _get_description(self, soup: BeautifulSoup, default_value: str) -> str:

        element = soup.select_one("div.Book-resume")
        return element.get_text(strip=True) if element else default_value

    async def _get_image_url(
        self, soup: BeautifulSoup, client: HttpClientBase, default_value: str = ""
    ) -> str:
        element = soup.select_one("div.Book-cover img:first-child")
        if not element:
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
        except Exception:
            self._logger.warning(
                f"Failed to fetch or encode image from URL: {url}. See above for details.",
            )

        return default_value

    def _get_prices(
        self, soup: BeautifulSoup, url: str, default_value: list[BookPrice] = []
    ) -> list[BookPrice]:
        element = soup.select_one("p.Book-price > span:last-child")
        gallimard_price: list[str] = (
            element.get_text(strip=True).split() if element else []
        )
        return (
            [
                BookPrice(
                    prix=float(gallimard_price[0]),
                    currency="EUR" if gallimard_price[1] == "€" else "",
                    url=url,
                    source="Gallimard Jeunesse",
                )
            ]
            if gallimard_price
            else []
        )

    # endregion

    def get_total_and_average_by_currency(self) -> dict[str, tuple[float, float]]:
        self._logger.info("Calculating total and average prices")
        books = self._repository.list()
        books_by_currency: dict[str, dict[str, float]] = {}
        for book in books:
            for price in book.prices:
                if not books_by_currency.get(price.currency):
                    books_by_currency[price.currency] = {"total": 0.0, "average": 0.0}

                books_by_currency[price.currency]["total"] += price.prix
                books_by_currency[price.currency]["average"] = (
                    books_by_currency[price.currency]["total"] / len(book.prices)
                    if book.prices
                    else 0.0
                )

        result: dict[str, tuple[float, float]] = {}
        for currency, values in books_by_currency.items():
            result[currency] = (values["total"], values["average"])
        return result
