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
        # arrange
        exceptions: list[Exception] = []
        tomes = []

        # find urls then load each book's data
        urls = await self.__book_usecases.find_urls()
        self.__logger.info(
            "Finding data for each book from html contents", self.__class__.__name__
        )

        async with httpx.AsyncClient() as async_client:
            tasks = [self.__book_usecases.load_async(url, async_client) for url in urls]
            for tome in await asyncio.gather(*tasks, return_exceptions=True):
                if isinstance(tome, Exception):
                    exceptions.append(tome)
                else:
                    tomes.append(tome)

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
        total = sum(t.prix for t in tomes)
        average = total / len(tomes) if tomes else 0.0
        return total, average
