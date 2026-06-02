import asyncio
from typing import Literal

from bs4 import BeautifulSoup

from domain import Book
from ports import BookRepositoryInterface, HttpClientBase
from usecases.BookUseCasesInterface import BookUseCasesInterface
from usecases.OfficialBookDetails import OfficialBookDetails


class OfficialBookUseCases(BookUseCasesInterface):
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        repository: BookRepositoryInterface,
        client: HttpClientBase,
        parallel_calls: int = 5,
    ):
        super().__init__(repository, client)
        self._parallel_calls = parallel_calls

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        results: list[Book] = []

        active_client = client or self._client
        async with active_client as client_instance:
            self._logger.info(f"Finding urls of books from {self._url_base}")
            urls = await self._fetch_book_urls(client_instance)

            self._logger.info(f"Fetching book details for {len(urls)} URLs")
            results: list[Book] = []
            for i in range(0, len(urls), self._parallel_calls):
                selected_urls = urls[i : i + self._parallel_calls]
                tasks = [self.fetch_book(url, client_instance) for url in selected_urls]
                results.extend([book for book in await asyncio.gather(*tasks) if book])

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
            json = await client.get_json(_build_full_url(segment))

            # parse HTML content to find book detail links
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

        return result

    # endregion

    async def fetch_book(
        self, url: str, client: HttpClientBase | None = None
    ) -> Book | None:
        book: Book | None = None
        numero_options = {"id": 0}
        try:
            self._logger.info(
                f"get book details from : {url}",
            )
            active_client = client or self._client
            html = await active_client.get_text(url)
            soup = BeautifulSoup(html, "html.parser")

            details = OfficialBookDetails(soup)
            authors = details.authors()
            if "Joe Dever" not in authors:
                self._logger.warning(
                    f"Skipping book at {url}. It doesn't match authors.",
                )
                return None

            id = numero = details.numero(numero_options)
            if numero < 0:
                self._logger.error(
                    f"Could not find a valid book's number at {url}. Defaulting to {numero_options['id']}.",
                )

            book = Book(
                id=id,
                url=url,
                numero=numero,
                titre=details.title(""),
                authors=authors,
                lastParutionDate=details.last_parution_date("1900-01-01"),
                description=details.description(""),
                isbn=details.isbn(""),
                image=await details.image_url(active_client),
                prices=details.prices(url, []),
                official=True,
            )
        except Exception as e:
            self._logger.error(
                f"Error while fetching book details for {url} - reason: {type(e).__name__}: {e}",
                exc_info=True,
            )

        return book

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
