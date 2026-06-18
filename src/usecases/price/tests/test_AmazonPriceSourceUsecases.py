import asyncio
from pathlib import Path
from typing import Literal

from adapters.usecase.amazon.AmazonPriceDetailsFinder import AmazonPriceDetailsFinder
from domain import Book
from ports.browser import BrowserInterface, HtmlElementActionInterface, PageHandlerInterface
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


class FakeHtmlElementAction(HtmlElementActionInterface[object, object]):
    def __init__(self, page: object, matching_title: str) -> None:
        super().__init__(page)
        self.matching_title = matching_title
        self.values: dict[str, bool | str] = {}
        self.clicks: list[str] = []

    async def wait_for(
        self,
        selector: str,
        *,
        retry: int = 3,
        timeout: float | None = 5.0,
        state: Literal["attached", "detached", "hidden", "visible"] | None = "attached",
        **kwargs,
    ) -> bool:
        has_text = kwargs.get("has_text")
        if has_text is None:
            return True
        return bool(has_text.search(self.matching_title))

    async def set_value(self, css: str, value: bool | str) -> bool | str | None:
        self.values[css] = value
        return value

    async def click(self, css: str) -> bool:
        self.clicks.append(css)
        return True


class FakePageHandler(PageHandlerInterface[object, object, object]):
    def __init__(self, html: str, matching_title: str) -> None:
        self.action = FakeHtmlElementAction(object(), matching_title)
        self._html = html
        self.closed = False
        self._current_url = BASE_URL

    async def wait_for_url_change(self, previous_url: str, timeout: int = 10000) -> bool:
        self._current_url = f"{BASE_URL}/s?k=fake"
        return True

    async def current_url(self) -> str:
        return self._current_url

    async def close(self) -> None:
        self.closed = True

    async def html(self) -> str:
        return self._html


class FakeBrowser(BrowserInterface[object, object, object]):
    def __init__(self, page: FakePageHandler) -> None:
        super().__init__()
        self.page = page
        self.contexts: list[int] = []
        self.opened = False

    async def __aenter__(self) -> "FakeBrowser":
        self.opened = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.opened = False

    async def start(self) -> None:
        self.opened = True

    async def close(self) -> None:
        self.opened = False

    async def new_context(self) -> int:
        self.contexts.append(0)
        return 0

    async def new_page(self, url: str, context_index: int = 0) -> FakePageHandler:
        return self.page


def test_fetch_bookprice_returns_amazon_price_from_dataset():
    book = make_book("9782075168694", "Les Maîtres des Ténèbres", 1)
    page = FakePageHandler(
        read_dataset("amazon_9782075168694.html"),
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
        read_dataset("amazon_9782075123211.html"),
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
        read_dataset("amazon_2070519031.html"),
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
        read_dataset("amazon_2070519031.html"),
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
