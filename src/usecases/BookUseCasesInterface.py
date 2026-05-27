from domain import Book
from ports import BookRepositoryInterface, FetcherInterface, LoggerInterface


class BookUseCasesInterface:
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        repository: BookRepositoryInterface,
        logger: LoggerInterface,
    ):
        self._repository = repository
        self._logger = logger

    async def fetch_books(self, fetcher: FetcherInterface) -> list[Book]:
        raise NotImplementedError

    async def fetch_book(
        self, url: str, fetcher: FetcherInterface, attempts: int = 3
    ) -> Book | None:
        raise NotImplementedError

    def get_total_and_average_by_currency(self) -> dict[str, tuple[float, float]]:
        raise NotImplementedError
