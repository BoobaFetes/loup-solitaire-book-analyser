from adapters import FetcherAdapter
from domain import Book
from ports import BookRepositoryInterface, FetcherInterface, LoggerInterface
from usecases.BookUseCasesInterface import BookUseCasesInterface
from usecases.NonOfficialBookUseCases import NonOfficialBookUseCases
from usecases.OfficialBookUseCases import OfficialBookUseCases


class BookUseCases(BookUseCasesInterface):
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        repository: BookRepositoryInterface,
        logger: LoggerInterface,
    ):
        super().__init__(repository, logger)
        self._official_book: BookUseCasesInterface = OfficialBookUseCases(
            repository, logger
        )
        self._non_official_book: BookUseCasesInterface = NonOfficialBookUseCases(
            repository, logger
        )

    async def fetch_books(self, fetcher=FetcherInterface()) -> list[Book]:
        books_sources: list[list[Book]] = []

        async with FetcherAdapter(self._logger) as _fetcher:
            books_sources.append(await self._official_book.fetch_books(_fetcher))
            books_sources.append(await self._non_official_book.fetch_books(_fetcher))

        books_set: set[Book] = set(books_sources[0])
        non_official_books_set: set[Book] = set(books_sources[1])

        # merge data from non official source into official books if they have the same number of book in the serie, otherwise add them as new entries
        # Fusionne les deux listes sans doublons (basé sur Book.id)
        books_set |= non_official_books_set
        books: list[Book] = list(books_set)
        # tri par id de livre (on s'attend à id==numero) pour simplifier la lecture et la maintenance
        books.sort(key=lambda b: b.id)

        self._logger.debug("records books in repository", self.__class__.__name__)
        self._repository.clear()
        added_count = self._repository.add_many(books)
        if added_count != len(books):
            self._logger.warning(
                "Not all books were added to the repository.", self.__class__.__name__
            )
            raise ValueError("Not all books were added to the repository.")

        return self._repository.list()

    async def fetch_book(
        self, url: str, fetcher: FetcherInterface, attempts: int = 3
    ) -> Book | None:
        raise NotImplementedError

    def get_total_and_average_by_currency(self) -> dict[str, tuple[float, float]]:
        self._logger.info(
            "Calculating total and average prices", self.__class__.__name__
        )
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
