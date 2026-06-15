import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from domain import Book, BookPrice
from ports import IFileSystem

TStoreDataConverter = TypeVar("TStoreDataConverter")


class Database:
    def __init__(self, fs: IFileSystem, connection_string: str):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__fs = fs
        self.__directory = Path(connection_string)
        self.__directory.mkdir(parents=True, exist_ok=True)

        self.book_store: Path = self.__directory / "books.data.json"
        self.price_store: Path = self.__directory / "prices.data.json"

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        """
        Start the database context.
        """
        self.__logger.info(f"Open Database from file_system at {self.__directory}")
        if not self.__fs.is_file_exists(str(self.book_store)):
            self.__logger.info(f"Creating new book store file at {self.book_store}")
            self.__fs.write_file(str(self.book_store), "{}")

        if not self.__fs.is_file_exists(str(self.price_store)):
            self.__logger.info(f"Creating new price store file at {self.price_store}")
            self.__fs.write_file(str(self.price_store), "{}")

    async def stop(self):
        """
        Stop the database context.
        """
        self.__logger.info(f"Close Database from file_system at {self.__directory}")

    async def read_book_store(self) -> dict[str, Book]:
        """Extrait les données des books depuis le système de fichiers.

        Returns:
            dict[str, Book]: Un dictionnaire de books extraits.
        """
        return await self.__read_store(
            self.book_store,
            lambda data: {key: Book(**item) for key, item in data.items()},
        )

    async def write_book_store(self, data: dict[str, Book]) -> None:
        return await self.__write_store(
            self.book_store,
            data,
            convert=lambda d: {
                key: book.model_dump(mode="json") for key, book in d.items()
            },
        )

    async def read_price_store(self) -> dict[str, list[BookPrice]]:
        """Extrait les données des book prices depuis le système de fichiers.

        Returns:
            dict[str, list[BookPrice]]: Un dictionnaire de book prices dont les clés sont les ISBN.
        Notes:
        La structure de données retournée est la suivante :
        ```
        {
            "isbn1": [BookPrice(...), BookPrice(...), ...],
            "isbn2": [BookPrice(...), BookPrice(...), ...],
            ...
        }
        ```
        """
        return await self.__read_store(
            self.price_store,
            lambda data: {
                key: [BookPrice(**item) for item in items]
                for key, items in data.items()
            },
        )

    async def write_price_store(self, data: dict[str, list[BookPrice]]) -> None:
        return await self.__write_store(
            self.price_store,
            data,
            convert=lambda d: {
                key: [price.model_dump(mode="json") for price in prices]
                for key, prices in d.items()
            },
        )

    async def __read_store(
        self, store: Path, convert: Callable[[dict[str, Any]], Any]
    ) -> dict[str, Any]:
        """Extrait les données depuis le système de fichiers.

        Args:
            store (Path): Le chemin du fichier de données à lire.

        Returns:
            dict[str, Any]: Un dictionnaire des données extraites.
        """
        _path = str(store)
        content = self.__fs.read_file(_path)
        data: dict[str, Any] = json.loads(content)

        result = convert(data)
        self.__logger.info(
            f"Extracted {len(result)} items from store '{store.stem}'",
        )
        return result

    async def __write_store(
        self,
        store: Path,
        data: TStoreDataConverter,
        convert: Callable[[TStoreDataConverter], Any],
    ) -> None:
        _path = str(store)
        converte_data = convert(data)
        self.__fs.write_file(_path, json.dumps(converte_data, indent=2))
        self.__logger.info(
            f"Wrote {len(converte_data)} items to store '{store.stem}'",
        )
