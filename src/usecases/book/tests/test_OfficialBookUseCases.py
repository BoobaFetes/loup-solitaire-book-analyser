import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import cast

from adapters.usecase.gallimard.GallimardBookDetailsFinder import (
    GallimardBookDetailsFinder,
)
from adapters.usecase.gallimard.GallimardBookListFinder import GallimardBookListFinder
from adapters.usecase.gallimard.GallimardPriceDetailsFinder import (
    GallimardPriceDetailsFinder,
)
from adapters.http.tests.fake import FakeHttpClient
from ports.usecase import (
    BookDetailsFinderBase,
    BookListFinderBase,
    PriceDetailsFinderBase,
)
from usecases.book.tests.fake import (
    FakeOfficialBookDetailsFinder,
    FakeOfficialBookListFinder,
    FakeOfficialPriceDetailsFinder,
)
from usecases.book.OfficialBookUseCases import OfficialBookUseCases

DATASET = Path(__file__).parent / "dataset"
BASE_URL = "https://www.gallimard-jeunesse.fr"


def read_dataset(name: str) -> str:
    return (DATASET / name).read_text(encoding="utf-8")


_list_factory = cast(Callable[[str], BookListFinderBase], FakeOfficialBookListFinder)
_details_factory = cast(
    Callable[[str], BookDetailsFinderBase], FakeOfficialBookDetailsFinder
)
_price_factory = cast(
    Callable[[str], PriceDetailsFinderBase], FakeOfficialPriceDetailsFinder
)


def details_finder_with_authors_error(html: str) -> FakeOfficialBookDetailsFinder:
    finder = FakeOfficialBookDetailsFinder(html)
    finder.stub_authors_exception(ValueError("broken"))
    return finder


def test_fetch_book_builds_official_book_from_gallimard_dataset():

    # Arrange
    url = f"{BASE_URL}/9782075168694/les-maitres-des-tenebres.html"
    use_cases = OfficialBookUseCases(
        BASE_URL,
        FakeHttpClient({url: read_dataset("gallimard_9782075168694.html")}),
        GallimardBookListFinder,
        GallimardBookDetailsFinder,
        GallimardPriceDetailsFinder,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = True
    assert actual.official is expected
    expected = "9782075168694"
    assert actual.isbn == expected
    expected = 1
    assert actual.numero == expected
    expected = "Les Maîtres des tenèbres"
    assert actual.titre == expected
    assert "Joe Dever" in actual.authors
    expected = "2022-03-03"
    assert actual.lastParutionDate == expected
    assert actual.prices[0].price == 16.5
    assert actual.prices[0].source == BASE_URL
    expected = ""
    assert actual.image == expected
    assert actual.imageSourceUrl.endswith(".jpg")
    expected = b"fake-image"
    assert actual.imageContent == expected


def test_fetch_book_ignores_page_when_author_is_not_joe_dever():

    # Arrange
    url = f"{BASE_URL}/not-joe-dever.html"
    html = (
        read_dataset("gallimard_9782075168694.html")
        .replace('title="Joe Dever">Joe', 'title="Autre Auteur">Autre', 1)
        .replace("<span>Dever</span>", "<span>Auteur</span>", 1)
    )
    use_cases = OfficialBookUseCases(
        BASE_URL,
        FakeHttpClient({url: html}),
        GallimardBookListFinder,
        GallimardBookDetailsFinder,
        GallimardPriceDetailsFinder,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is expected


def test_fetch_book_urls_warms_gallimard_catalogue_session_before_fragment():

    # Arrange
    fragment_url = f"{BASE_URL}/catalogue/fragment?page=1&text=loup%20solitaire"
    referer = f"{BASE_URL}/catalogue.html?text=loup+solitaire"
    client = FakeHttpClient(
        text_by_endpoint={referer: "<html></html>"},
        json_by_endpoint={fragment_url: {"html": "", "next-url": False}},
    )
    use_cases = OfficialBookUseCases(
        BASE_URL,
        client,
        GallimardBookListFinder,
        GallimardBookDetailsFinder,
        GallimardPriceDetailsFinder,
    )

    # Act
    actual = asyncio.run(use_cases._fetch_book_urls(client))
    text_headers = client.text_requests[0][1]
    json_headers = client.json_requests[0][1]

    # Assert
    expected = []
    assert actual == expected
    assert client.cache_enabled is True
    assert client.text_requests[0][0] == referer
    assert text_headers is not None
    assert text_headers["Sec-Fetch-Mode"] == "navigate"
    assert client.json_requests[0][0] == fragment_url
    assert json_headers is not None
    assert json_headers["Referer"] == referer
    assert json_headers["X-Requested-With"] == "XMLHttpRequest"


def test_fetch_books_reads_paginated_fragments_and_fetches_details():

    # Arrange
    first_fragment = f"{BASE_URL}/catalogue/fragment?page=1&text=loup%20solitaire"
    second_fragment = f"{BASE_URL}/catalogue/fragment?page=2&text=loup%20solitaire"
    referer = f"{BASE_URL}/catalogue.html?text=loup+solitaire"
    book_url = f"{BASE_URL}/book-1.html"
    client = FakeHttpClient(
        text_by_endpoint={referer: "<catalogue>", book_url: "<details>"},
        json_by_endpoint={
            first_fragment: {
                "html": "<page-1>",
                "next-url": "/catalogue/fragment?page=2&text=loup%20solitaire",
            },
            second_fragment: {"html": "<page-2>", "next-url": False},
        },
    )
    use_cases = OfficialBookUseCases(
        BASE_URL,
        client,
        _list_factory,
        _details_factory,
        _price_factory,
        parallel_calls=1,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_books())

    # Assert
    assert [book.numero for book in actual] == [4, 4]
    actual = len(client.json_requests)

    expected = 2
    assert actual == expected
    assert client.opened is False


def test_fetch_book_returns_none_for_empty_html_and_handles_no_price_or_negative_numero():

    # Arrange
    empty_url = f"{BASE_URL}/empty.html"
    no_price_url = f"{BASE_URL}/no-price.html"
    negative_url = f"{BASE_URL}/negative.html"
    use_cases = OfficialBookUseCases(
        BASE_URL,
        FakeHttpClient(
            {
                empty_url: "",
                no_price_url: "no-price",
                negative_url: "negative",
            }
        ),
        _list_factory,
        _details_factory,
        _price_factory,
    )

    # Act
    empty = asyncio.run(use_cases.fetch_book(empty_url))
    no_price = asyncio.run(use_cases.fetch_book(no_price_url))
    negative = asyncio.run(use_cases.fetch_book(negative_url))

    # Assert
    assert empty is None
    assert no_price is not None
    assert no_price.prices == []
    assert negative is not None
    assert negative.numero == -1


def test_fetch_book_returns_none_when_details_raise():

    # Arrange
    url = f"{BASE_URL}/error.html"

    use_cases = OfficialBookUseCases(
        BASE_URL,
        FakeHttpClient({url: "<html>"}),
        _list_factory,
        cast(Callable[[str], BookDetailsFinderBase], details_finder_with_authors_error),
        _price_factory,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is expected
