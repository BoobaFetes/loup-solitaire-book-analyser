import asyncio
from pathlib import Path

from adapters.usecase.gallimard.GallimardPriceDetailsFinder import (
    GallimardPriceDetailsFinder,
)
from domain import Book
from ports.http import HttpClientBase
from usecases.price.GallimardPriceSourceUsecases import GallimardPriceSourceUsecases

DATASET = Path(__file__).parent / "dataset"
BASE_URL = "https://www.gallimard-jeunesse.fr"


def read_dataset(name: str) -> str:
    return (DATASET / name).read_text(encoding="utf-8")


def make_book(isbn: str, titre: str, url: str) -> Book:
    return Book(
        id=1,
        url=url,
        isbn=isbn,
        numero=1,
        titre=titre,
        authors=["Joe Dever"],
    )


class FakeHttpClient(HttpClientBase[object, object]):
    def __init__(self, texts: dict[str, str] | None = None) -> None:
        self.texts = texts or {}
        self.opened = False

    async def open(self, **kwargs) -> None:
        self.opened = True

    async def close(self) -> None:
        self.opened = False

    async def get_text(
        self, endpoint: str, encoding: str | None = None, retry: int = 3
    ) -> str:
        return self.texts.get(endpoint, "")


def test_fetch_bookprice_returns_gallimard_price_from_dataset():
    url = f"{BASE_URL}/9782075168694/les-maitres-des-tenebres.html"
    book = make_book("9782075168694", "Les Maîtres des tenèbres", url)
    use_cases = GallimardPriceSourceUsecases(
        FakeHttpClient({url: read_dataset("gallimard_9782075168694.html")}),
        BASE_URL,
        GallimardPriceDetailsFinder,
    )

    price = asyncio.run(use_cases.fetch_bookprice(book))

    assert price is not None
    assert price.isbn == "9782075168694"
    assert price.source == BASE_URL
    assert price.price == 16.5
    assert price.currency == "€"
    assert price.url == url


def test_fetch_bookprice_returns_none_when_html_is_empty():
    url = f"{BASE_URL}/missing.html"
    book = make_book("2070519031", "Sur la Piste du Loup", url)
    use_cases = GallimardPriceSourceUsecases(
        FakeHttpClient({url: ""}),
        BASE_URL,
        GallimardPriceDetailsFinder,
    )

    price = asyncio.run(use_cases.fetch_bookprice(book))

    assert price is None


def test_fetch_bookprice_returns_none_when_gallimard_has_no_price():
    url = f"{BASE_URL}/2070519031/sur-la-piste-du-loup.html"
    book = make_book("2070519031", "Sur la Piste du Loup", url)
    use_cases = GallimardPriceSourceUsecases(
        FakeHttpClient({url: read_dataset("gallimard_fake_no_price.html")}),
        BASE_URL,
        GallimardPriceDetailsFinder,
    )

    price = asyncio.run(use_cases.fetch_bookprice(book))

    assert price is not None
    assert price.isbn == "2070519031"
    assert price.source == BASE_URL
    assert price.price == 0.0
    assert price.currency == "not set"
    assert price.url == url
