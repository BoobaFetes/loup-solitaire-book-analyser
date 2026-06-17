from typing import Literal, Protocol, TypeVar

from domain import BookPrice
from ports.database.IRepository import IRepository

TId = TypeVar("TId", bound=tuple[str, str], contravariant=True)

TBookPriceListField = Literal["isbn", "source", "date"]


class IBookPriceRepository(IRepository[BookPrice, TId, TBookPriceListField], Protocol):
    async def dict_last_price_of_source_by_isbns(
        self,
        sources: list[str],
        isbns: list[str] = [],
    ) -> dict[str, dict[str, BookPrice | None]]:
        """
        Retourne un dictionnaire des derniers prix par source pour une liste d'ISBN donnée.

        :param sources: La liste des sources.
        :param isbns: La liste des ISBN des livres.

        :return: Un dictionnaire des derniers prix par source pour les ISBN donnés.
        """
        ...

    async def dict_by_isbns(self, isbns: list[str] = []) -> dict[str, list[BookPrice]]:
        """
        Retourne un dictionnaire de book prices pour une liste d'ISBN donnée.

        :param isbns: La liste des ISBN des livres.

        :return: Un dictionnaire de book prices pour les ISBN donnés.
        """
        ...
