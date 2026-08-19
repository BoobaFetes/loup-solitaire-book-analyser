import asyncio
from pathlib import Path

from adapters.browser.tests.fake import FakeBrowser, FakePageHandler
from adapters.usecase.amazon.AmazonPriceDetailsFinder import AmazonPriceDetailsFinder
from domain import Book
from usecases.price.AmazonPriceSourceUsecases import AmazonPriceSourceUsecases

DATASET = Path(__file__).parent / "dataset"
BASE_URL = "https://www.amazon.fr"
CACHE_DIR = "caches"


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


def test_fetch_bookprice_returns_amazon_price_from_dataset(tmp_path):

    # Arrange
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

    # Act
    actual = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = "9782075168694"
    assert actual.isbn == expected
    expected = BASE_URL
    assert actual.source == expected
    expected = "€"
    assert actual.currency == expected
    assert actual.price > 0
    assert page.closed is True


def test_fetch_bookprice_matches_agarash_title_with_apostrophe_variant(tmp_path):

    # Arrange
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

    # Act
    actual = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = "9782075123211"
    assert actual.isbn == expected
    assert actual.price > 0
    expected = "€"
    assert actual.currency == expected


def test_fetch_bookprice_returns_not_set_price_for_gallimard_missing_book_without_visible_amazon_price(
    tmp_path,
):
    # Arrange
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

    # Act
    actual = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

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
    assert "2070519031" in actual.url


def test_fetch_bookprice_returns_none_when_amazon_result_is_not_visible(tmp_path):

    # Arrange
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

    # Act
    actual = asyncio.run(
        use_cases.fetch_bookprice(book, browser=FakeBrowser(page), context_index=0)
    )

    # Assert
    expected = None
    assert actual is expected
    assert page.closed is True


def test_fetch_bookprices_uses_browser_context_and_returns_found_prices(tmp_path):

    # Arrange
    book = make_book("9782075168694", "Les Maîtres des Ténèbres", 1)
    page = FakePageHandler(
        html=read_dataset("amazon_9782075168694.html"),
        matching_title="Les Maîtres des Ténèbres",
    )
    browser = FakeBrowser(page)
    use_cases = AmazonPriceSourceUsecases(
        BASE_URL,
        AmazonPriceDetailsFinder,
        browser,
        request_delay_seconds=0,
    )

    actual = asyncio.run(use_cases.fetch_bookprices([book]))

    # Act
    actual_count = len(actual)

    # Assert
    expected = 1
    assert actual_count == expected
    expected = "9782075168694"
    assert actual[0].isbn == expected
    assert browser.opened is False
    assert browser.new_context_options == [{}]


def test_fetch_bookprice_rejects_missing_browser_parameters(tmp_path):

    # Arrange
    book = make_book("9782075168694", "Les Maîtres des Ténèbres", 1)
    use_cases = AmazonPriceSourceUsecases(
        BASE_URL,
        AmazonPriceDetailsFinder,
        FakeBrowser(),
        request_delay_seconds=0,
    )

    # Act
    try:
        asyncio.run(use_cases.fetch_bookprice(book))
    except ValueError as error:
        # Assert
        assert "browser must be" in str(error)
    else:
        raise AssertionError("ValueError was not raised")

    # Act
    try:
        asyncio.run(use_cases.fetch_bookprice(book, browser=FakeBrowser()))
    except ValueError as error:
        # Assert
        assert "context_index" in str(error)
    else:
        raise AssertionError("ValueError was not raised")
