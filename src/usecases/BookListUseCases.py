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
        # arrange
        books_sources: list[list[Book]] = []

        # action
        self._logger.info("Fetching books from sources")
        active_client = client or self._client
        async with active_client as client_instance:
            books_sources.append(await self._official_book.fetch_books(client_instance))
            books_sources.append(
                await self._non_official_book.fetch_books(client_instance)
            )

        books: list[Book]=self.__merge_sources(books_sources[0], books_sources[1])

        # tri par id de livre (on s'attend à id==numero) pour simplifier la lecture et la maintenance
        books.sort(key=lambda b: b.id)

        self._logger.info("records books in repository")
        added_count = self._repository.upsert_many(books)
        if added_count != len(books):
            self._logger.warning("Not all books were upserted to the repository.")

        return self._repository.list()

    def __merge_sources(
        self, official_books: list[Book], non_official_books: list[Book]
    ) -> list[Book]:
        def get_book_by_numero(
            numero: int, official: list[Book], non_official: list[Book]
        ) -> tuple[Book, Book]:
            official_book = [book for book in official if book.numero == numero]
            non_official_book = [book for book in non_official if book.numero == numero]

            if not official_book or not non_official_book:
                raise ValueError(
                    f"Book with numero {numero} not found in one of the sources"
                )

            return (official_book[0], non_official_book[0])

        # fix official source issues from non official source
        (book_1_official, book_1_non_official) = get_book_by_numero(
            1, official_books, non_official_books
        )
        book_1_official.titre = book_1_non_official.titre

        # merge non official books into official books if they have the same numero, otherwise add them as new entries 
        # (based on Book.__hash__ and Book.__eq__ which are based on Book.id)
        books_set: set[Book] = set(official_books)
        books_set |= set(non_official_books)  

        return list(books_set)

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

                books_by_currency[price.currency]["total"] += price.price
                books_by_currency[price.currency]["average"] = (
                    books_by_currency[price.currency]["total"] / len(book.prices)
                    if book.prices
                    else 0.0
                )

        result: dict[str, tuple[float, float]] = {}
        for currency, values in books_by_currency.items():
            result[currency] = (values["total"], values["average"])
        return result
