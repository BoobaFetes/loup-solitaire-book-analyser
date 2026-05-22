import asyncio
from typing import Tuple

import httpx

from domain import Book
from ports import (
    BookRepositoryInterface,
    LoggerInterface,
)
from usecases import BookUseCases


class MainUseCases:
    """Main use cases for the application."""

    Url_of_list_of_books: str = (
        "https://www.bibliotheque-des-aventuriers.com/menu/4_serie/loup_solitaire.htm"
    )

    def __init__(
        self,
        book_usecases: BookUseCases,
        repo: BookRepositoryInterface,
        logger: LoggerInterface,
    ):
        self.__book_usecases = book_usecases
        self.__repo = repo
        self.__logger: LoggerInterface = logger

    async def download_tomes(self) -> list[Book]:
        """Downloads all tomes from the source.

        Raises:
            ValueError: If the book data is invalid or if the book repository is not found.

        Returns:
            list[Book]: A list of downloaded books.
        """
        # arrange
        exceptions: list[Exception] = []
        tomes: list[Book] = []
        self.__logger.info("downloading tomes asynchronously", self.__class__.__name__)

        # find urls then load each book's data
        async with httpx.AsyncClient() as async_client:
            urls = await self.__book_usecases.find_urls_async(async_client)
            tasks = [self.__book_usecases.load_async(url, async_client) for url in urls]
            for tome in await asyncio.gather(*tasks, return_exceptions=True):
                if isinstance(tome, Book):
                    tomes.append(tome)
                else:
                    exceptions.append(tome)  # type: ignore

        if exceptions:
            raise ValueError(
                f"Errors occurred during parsing: {len(exceptions)} errors. See logs for details."
            )

        # save tomes in repository
        add_count = self.__repo.add_many(tomes)
        if add_count != len(tomes):
            self.__logger.warning(
                "Not all tomes were added to the repository.", self.__class__.__name__
            )
            raise ValueError("Not all tomes were added to the repository.")

        return tomes

    def get_total_and_average(self) -> Tuple[float, float]:
        self.__logger.info(
            "Calculating total and average prices", self.__class__.__name__
        )
        tomes = self.__repo.list()
        total = 0.0
        for book in tomes:
            total += sum([price.prix for price in book.prices])
        average = total / len(tomes) if tomes else 0.0
        return total, average
