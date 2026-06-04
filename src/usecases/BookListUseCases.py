import logging

from domain import Book
from ports import BookRepositoryInterface, HttpClientBase
from usecases.book_list import NonOfficialBookUseCases, OfficialBookUseCases


class BookListUseCases:
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        repository: BookRepositoryInterface,
        client: HttpClientBase,
        official_book: OfficialBookUseCases,
        non_official_book: NonOfficialBookUseCases,
    ):
        self._repository = repository
        self._client = client
        self._logger = logging.getLogger(self.__class__.__name__)
        self._official_book: OfficialBookUseCases = official_book
        self._non_official_book: NonOfficialBookUseCases = non_official_book

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        books_sources: list[list[Book]] = []

        self._logger.info("Fetching books from sources")
        active_client = client or self._client
        async with active_client as client_instance:
            books_sources.append(await self._official_book.fetch_books(client_instance))
            books_sources.append(
                await self._non_official_book.fetch_books(client_instance)
            )

        books_set: set[Book] = set(books_sources[0])
        non_official_books_set: set[Book] = set(books_sources[1])

        # merge data from non official source into official books if they have the same number of book in the serie, otherwise add them as new entries
        # Fusionne les deux listes sans doublons (basé sur Book.id)
        books_set |= non_official_books_set
        books: list[Book] = list(books_set)

        # tri par id de livre (on s'attend à id==numero) pour simplifier la lecture et la maintenance
        books.sort(key=lambda b: b.id)

        self._logger.info("records books in repository")
        self._repository.clear()
        added_count = self._repository.add_many(books)
        if added_count != len(books):
            self._logger.warning("Not all books were added to the repository.")
            raise ValueError("Not all books were added to the repository.")

        return self._repository.list()

    async def list(self) -> list[Book]:
        return self._repository.list()

    async def get(self, *, id: int, isbn: str) -> Book:
        data = await self.find(id=id, isbn=isbn)
        if not data:
            raise ValueError(f"Book with id {id} or isbn {isbn} not found")
        return data

    async def find(self, *, id: int, isbn: str) -> Book | None:
        data = self._repository.list()
        if id:
            data = [book for book in data if book.id == id]
        elif isbn:
            data = [book for book in data if book.isbn == isbn]

        return None

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
