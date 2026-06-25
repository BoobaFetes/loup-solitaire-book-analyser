import asyncio
from pathlib import Path

from adapters.usecase.amazon.AmazonPriceDetailsFinder import AmazonPriceDetailsFinder
from adapters.browser.tests.fake import FakeBrowser, FakePageHandler
from domain import Book
from usecases.price.AmazonPriceSourceUsecases import AmazonPriceSourceUsecases

DATASET = Path(__file__).parent / "dataset"
BASE_URL = "https://www.amazon.fr"


def read_dataset(name: str) -> str:
    return (DATASET / name).read_text(encoding="utf-8")


def make_book(isbn: str, titre: str, numero: int) -> Book:
    return Book(
        id=numero,
        url=f"https://book.test/{isbn}",
        isbn=isbn,
        numero=numero,
        titre=titre,
        authors=["Joe Dever"],
    )


def test_fetch_bookprice_returns_amazon_price_from_dataset():
    book = make_book("9782075168694", "Les Maîtres des Ténèbres", 1)
    page = FakePageHandler(
        html=read_dataset("amazon_9782075168694.html"),
        matching_title="Les Maîtres des Ténèbres",
    )
    use_cases = AmazonPriceSourceUsecases(
        BASE_URL,
        AmazonPriceDetailsFinder,
        FakeBrowser(page),
        request_delay_seconds=0,
    )

    price = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

    assert price is not None
    assert price.isbn == "9782075168694"
    assert price.source == BASE_URL
    assert price.currency == "€"
    assert price.price > 0
    assert page.closed is True


def test_fetch_bookprice_matches_agarash_title_with_apostrophe_variant():
    book = make_book("9782075123211", "L'œil d'Agarash", 0)
    page = FakePageHandler(
        html=read_dataset("amazon_9782075123211.html"),
        matching_title="L'Œil d'Agarash",
    )
    use_cases = AmazonPriceSourceUsecases(
        BASE_URL,
        AmazonPriceDetailsFinder,
        FakeBrowser(page),
        request_delay_seconds=0,
    )

    price = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

    assert price is not None
    assert price.isbn == "9782075123211"
    assert price.price > 0
    assert price.currency == "€"


def test_fetch_bookprice_returns_not_set_price_for_gallimard_missing_book_without_visible_amazon_price():
    book = make_book("2070519031", "Sur la Piste du Loup", 25)
    page = FakePageHandler(
        html=read_dataset("amazon_2070519031.html"),
        matching_title="Sur la Piste du Loup",
    )
    use_cases = AmazonPriceSourceUsecases(
        BASE_URL,
        AmazonPriceDetailsFinder,
        FakeBrowser(page),
        request_delay_seconds=0,
    )

    price = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

    assert price is not None
    assert price.isbn == "2070519031"
    assert price.source == BASE_URL
    assert price.price == 0.0
    assert price.currency == "not set"
    assert "2070519031" in price.url


def test_fetch_bookprice_returns_none_when_amazon_result_is_not_visible():
    book = make_book("2070519031", "Sur la Piste du Loup", 25)
    page = FakePageHandler(
        html=read_dataset("amazon_2070519031.html"),
        matching_title="Un autre livre",
    )
    use_cases = AmazonPriceSourceUsecases(
        BASE_URL,
        AmazonPriceDetailsFinder,
        FakeBrowser(page),
        request_delay_seconds=0,
    )

    price = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

    assert price is None
    assert page.closed is True
