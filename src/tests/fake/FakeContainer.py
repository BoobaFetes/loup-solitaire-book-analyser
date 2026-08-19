from domain import Book
from adapters.cache.tests.fake import FakeInMemoryCache
from adapters.database.tests.fake import FakeUnitOfWork
from tests.fake.FakeBookListUseCases import FakeBookListUseCases
from tests.fake.FakeBookPriceUseCases import FakeBookPriceUseCases
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeContainer(SpyStubFake):
    def __init__(self, books: list[Book]) -> None:
        super().__init__()
        self.cache = FakeInMemoryCache()
        self.book_list = FakeBookListUseCases(books)
        self.book_prices = FakeBookPriceUseCases(books)

    def stub_unit_of_work(self, returned: FakeUnitOfWork) -> None:
        self._stub("unit_of_work", returned)

    @property
    def spy_unit_of_work(self) -> list[SpyCall]:
        return self._spy("unit_of_work")

    def stub_book_list_usecases(self, returned: FakeBookListUseCases) -> None:
        self._stub("book_list_usecases", returned)

    @property
    def spy_book_list_usecases(self) -> list[SpyCall]:
        return self._spy("book_list_usecases")

    def stub_book_price_usecases(self, returned: FakeBookPriceUseCases) -> None:
        self._stub("book_price_usecases", returned)

    @property
    def spy_book_price_usecases(self) -> list[SpyCall]:
        return self._spy("book_price_usecases")

    def stub_inmemory_cache(self, returned: FakeInMemoryCache) -> None:
        self._stub("inmemory_cache", returned)

    @property
    def spy_inmemory_cache(self) -> list[SpyCall]:
        return self._spy("inmemory_cache")

    def unit_of_work(self) -> FakeUnitOfWork:
        returned = self._returned_or_default("unit_of_work", FakeUnitOfWork())
        return self._record_call("unit_of_work", (), {}, returned)

    def book_list_usecases(self) -> FakeBookListUseCases:
        returned = self._returned_or_default("book_list_usecases", self.book_list)
        return self._record_call("book_list_usecases", (), {}, returned)

    def book_price_usecases(self) -> FakeBookPriceUseCases:
        returned = self._returned_or_default("book_price_usecases", self.book_prices)
        return self._record_call("book_price_usecases", (), {}, returned)

    def inmemory_cache(self) -> FakeInMemoryCache:
        returned = self._returned_or_default("inmemory_cache", self.cache)
        return self._record_call("inmemory_cache", (), {}, returned)
