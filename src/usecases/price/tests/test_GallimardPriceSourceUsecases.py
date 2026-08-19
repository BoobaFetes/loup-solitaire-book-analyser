import asyncio
from pathlib import Path

from adapters.usecase.gallimard.GallimardPriceDetailsFinder import (
    GallimardPriceDetailsFinder,
)
from domain import Book
from adapters.http.tests.fake import FakeHttpClient
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


def test_fetch_bookprice_returns_gallimard_price_from_dataset():

    # Arrange
    url = f"{BASE_URL}/9782075168694/les-maitres-des-tenebres.html"
    book = make_book("9782075168694", "Les Maîtres des tenèbres", url)
    use_cases = GallimardPriceSourceUsecases(
        FakeHttpClient({url: read_dataset("gallimard_9782075168694.html")}),
        BASE_URL,
        GallimardPriceDetailsFinder,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_bookprice(book))

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = "9782075168694"
    assert actual.isbn == expected
    expected = BASE_URL
    assert actual.source == expected
    expected = 16.5
    assert actual.price == expected
    expected = "€"
    assert actual.currency == expected
    expected = url
    assert actual.url == expected


def test_fetch_bookprice_returns_none_when_html_is_empty():

    # Arrange
    url = f"{BASE_URL}/missing.html"
    book = make_book("2070519031", "Sur la Piste du Loup", url)
    use_cases = GallimardPriceSourceUsecases(
        FakeHttpClient({url: ""}),
        BASE_URL,
        GallimardPriceDetailsFinder,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_bookprice(book))

    # Assert
    expected = None
    assert actual is expected


def test_fetch_bookprice_returns_none_when_gallimard_has_no_price():

    # Arrange
    url = f"{BASE_URL}/2070519031/sur-la-piste-du-loup.html"
    book = make_book("2070519031", "Sur la Piste du Loup", url)
    use_cases = GallimardPriceSourceUsecases(
        FakeHttpClient({url: read_dataset("gallimard_fake_no_price.html")}),
        BASE_URL,
        GallimardPriceDetailsFinder,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_bookprice(book))

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = "2070519031"
    assert actual.isbn == expected
    expected = BASE_URL
    assert actual.source == expected
    expected = 0.0
    assert actual.price == expected
    expected = "not set"
    assert actual.currency == expected
    expected = url
    assert actual.url == expected


def test_fetch_bookprices_fetches_prices_in_parallel_batches():

    # Arrange
    first_url = f"{BASE_URL}/9782075168694/les-maitres-des-tenebres.html"
    second_url = f"{BASE_URL}/2070519031/sur-la-piste-du-loup.html"
    first = make_book("9782075168694", "Les Maîtres des tenèbres", first_url)
    second = make_book("2070519031", "Sur la Piste du Loup", second_url)
    client = FakeHttpClient(
        {
            first_url: read_dataset("gallimard_9782075168694.html"),
            second_url: "",
        }
    )
    use_cases = GallimardPriceSourceUsecases(
        client,
        BASE_URL,
        GallimardPriceDetailsFinder,
        parallel_calls=1,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_bookprices([first, second]))

    # Assert
    assert [price.isbn for price in actual] == ["9782075168694"]
    assert client.opened is False


def test_fetch_bookprice_returns_none_when_details_factory_raises():

    # Arrange
    url = f"{BASE_URL}/broken.html"
    book = make_book("9782075168694", "Les Maîtres des tenèbres", url)

    def broken_factory(html: str):
        raise ValueError("broken")

    use_cases = GallimardPriceSourceUsecases(
        FakeHttpClient({url: "<html>"}),
        BASE_URL,
        broken_factory,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_bookprice(book))

    # Assert
    expected = None
    assert actual is expected
