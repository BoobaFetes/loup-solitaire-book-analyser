import copy
import logging

from domain import Book, BookPrice
from ports import BookRepositoryInterface, HttpClientBase
from usecases.price_sources import PriceSourceUsecasesBase


class BookPriceUseCases:
    """Use cases for managing books."""

    _url_base: str = "https://www.gallimard-jeunesse.fr"

    def __init__(
        self,
        repository: BookRepositoryInterface,
        client: HttpClientBase,
        sources: list[PriceSourceUsecasesBase],
    ):
        self._repository = repository
        self._client = client
        self._logger = logging.getLogger(self.__class__.__name__)
        self._sources: list[PriceSourceUsecasesBase] = sources

    async def fetch_prices(self, books: list[Book]) -> list[BookPrice]:
        results: list[BookPrice] = []
        isbns = [book.isbn for book in books]

        async with self._client as client:
            for source in self._sources:
                self._logger.info(f"Fetching prices from {source.url_base}")
                results.extend(await source.fetch_bookprices(isbns, client))

        return results

    def bind_prices_to_books(
        self, books: list[Book], prices: list[BookPrice]
    ) -> list[Book]:
        # on ne veut surtout pas toucher à les référence fournies en paramètres, on DOIT ETRE idempotent !
        results = copy.deepcopy(books)
        data = copy.deepcopy(prices)

        self._logger.info("bind each price to its book")
        for book in results:
            # step 1 : on clone la liste afin de pouvoir la réduire dès qu'un prix est affecté à un livre (performance)
            remaining_prices = [*data]

            # step 2 : on affecte les prix du livre actuel à ce livre et on le retire de la liste des prix à affecter
            for price in remaining_prices:
                if price.isbn != book.isbn:
                    continue

                successfully_added = book.add_price(price)
                if successfully_added:
                    # on retire le prix de la liste des prix à affecter pour des raison de performance et pour éviter de l'affecter à un autre livre par erreur (dans le cas où il y aurait des prix avec des isbn incorrects ou manquants)
                    data.remove(price)
                else:
                    self._logger.warning(
                        f"Price {price} was not added to book {book}. This may be due to incorrect or missing ISBNs in the price data."
                    )

        # step 3: il faut prevenir si des prix n'ont pu etre affecté afin de permettre au developppeurs d'effectuer les correction nécessaire.
        if data:
            # dans un context asynchrone il est important de logger en une seule fois pour garantir la cohérence du message en vu de maintenance
            self._logger.warning(
                "\n".join(
                    [
                        "Some prices were not affected to any book and will be ignored. This may be due to incorrect or missing ISBNs in the price data.",
                        f"Remaining prices count: {len(data)} :",
                    ]
                    + [f" - {price}" for price in data]
                )
            )

        update_count = self._repository.update_many(results)
        if update_count != len(results):
            self._logger.error(
                "Not all books were updated in the repository after binding prices."
            )
        return results

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
