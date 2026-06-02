import logging

from domain import Book
from ports import BookRepositoryInterface, HttpClientBase


class BookUseCasesInterface:
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        repository: BookRepositoryInterface,
        client: HttpClientBase,
    ) -> None:
        self._repository = repository
        self._client = client
        self._logger = logging.getLogger(self.__class__.__name__)

    async def fetch_books(self, client: HttpClientBase | None = None) -> list[Book]:
        raise NotImplementedError

    async def fetch_book(
        self, url: str, client: HttpClientBase | None = None
    ) -> Book | None:
        raise NotImplementedError

    def get_total_and_average_by_currency(self) -> dict[str, tuple[float, float]]:
        raise NotImplementedError
