import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import cast

from adapters.usecase.biblio_aventurier.BiblioAventurierBookDetailsFinder import (
    BiblioAventurierBookDetailsFinder,
)
from adapters.usecase.biblio_aventurier.BiblioAventurierBookListFinder import (
    BiblioAventurierBookListFinder,
)
from adapters.http.tests.fake import FakeHttpClient
from ports.usecase import BookDetailsFinderBase, BookListFinderBase
from usecases.book.tests.fake import (
    FakeNonOfficialBookDetailsFinder,
    FakeNonOfficialBookListFinder,
)
from usecases.book.NonOfficialBookUseCases import NonOfficialBookUseCases

DATASET = Path(__file__).parent / "dataset"
BASE_URL = "https://www.bibliotheque-des-aventuriers.com/"


def read_dataset(name: str) -> str:
    return (DATASET / name).read_text(encoding="utf-8", errors="replace")


def make_use_cases(client: FakeHttpClient) -> NonOfficialBookUseCases:
    return NonOfficialBookUseCases(
        BASE_URL,
        client,
        BiblioAventurierBookListFinder,
        BiblioAventurierBookDetailsFinder,
    )


_list_factory = cast(Callable[[str], BookListFinderBase], FakeNonOfficialBookListFinder)
_details_factory = cast(
    Callable[[str], BookDetailsFinderBase], FakeNonOfficialBookDetailsFinder
)


def details_finder_with_numero_error(html: str) -> FakeNonOfficialBookDetailsFinder:
    finder = FakeNonOfficialBookDetailsFinder(html)
    finder.stub_numero_exception(ValueError("broken"))
    return finder


def test_fetch_book_builds_non_official_book_from_biblio_dataset():

    # Arrange
    url = f"{BASE_URL}serie/loup_solitaire/02_traversee_infernale.htm"
    use_cases = make_use_cases(
        FakeHttpClient({url: read_dataset("biblio_aventurier_9782075123181.html")})
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = False
    assert actual.official is expected
    expected = "9782075123181"
    assert actual.isbn == expected
    expected = 2
    assert actual.numero == expected
    expected = "La Traversée Infernale"
    assert actual.titre == expected
    assert "Joe Dever" in actual.authors
    expected = ""
    assert actual.image == expected
    assert actual.imageSourceUrl.lower().endswith(".jpg")
    expected = b"fake-image"
    assert actual.imageContent == expected


def test_fetch_book_ignores_classic_version():

    # Arrange
    url = f"{BASE_URL}serie/loup_solitaire/01_maitres_tenebres_classique.htm"
    use_cases = make_use_cases(
        FakeHttpClient(
            {
                url: read_dataset(
                    "biblio_aventurier_fake_maitres_tenebres_classique.html"
                )
            }
        )
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is expected


def test_fetch_book_accepts_augmented_version():

    # Arrange
    url = f"{BASE_URL}serie/loup_solitaire/01_maitres_tenebres_augmentee.htm"
    use_cases = make_use_cases(
        FakeHttpClient({url: read_dataset("biblio_aventurier_9782075168694.html")})
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = "9782075168694"
    assert actual.isbn == expected
    expected = 1
    assert actual.numero == expected
    expected = "Les Maîtres des Ténèbres"
    assert actual.titre == expected


def test_fetch_book_accepts_book_missing_from_gallimard_source():

    # Arrange
    url = f"{BASE_URL}serie/loup_solitaire/25_piste_loup.htm"
    use_cases = make_use_cases(
        FakeHttpClient({url: read_dataset("biblio_aventurier_2070519031.html")})
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = "2070519031"
    assert actual.isbn == expected
    expected = 25
    assert actual.numero == expected
    expected = "Sur la Piste du Loup"
    assert actual.titre == expected
    expected = url
    assert actual.url == expected
    expected = False
    assert actual.official is expected


def test_fetch_books_fetches_urls_in_parallel_batches():

    # Arrange
    client = FakeHttpClient(
        {
            f"{BASE_URL}menu/4_serie/loup_solitaire.htm": "<index>",
            f"{BASE_URL}book-1.html": "<details>",
            f"{BASE_URL}book-2.html": "<details>",
        }
    )
    use_cases = NonOfficialBookUseCases(
        BASE_URL,
        client,
        _list_factory,
        _details_factory,
        parallel_calls=1,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_books())

    # Assert
    assert [book.numero for book in actual] == [7, 7]
    assert client.opened is False


def test_fetch_book_urls_returns_empty_list_when_index_html_is_empty():

    # Arrange
    client = FakeHttpClient({f"{BASE_URL}menu/4_serie/loup_solitaire.htm": ""})
    use_cases = NonOfficialBookUseCases(
        BASE_URL, client, _list_factory, _details_factory
    )

    # Act
    actual = asyncio.run(use_cases._fetch_book_urls(client))

    # Assert
    expected = []
    assert actual == expected


def test_fetch_book_returns_none_when_html_is_empty_or_details_raise():

    # Arrange
    empty_url = f"{BASE_URL}empty.html"
    error_url = f"{BASE_URL}error.html"

    empty_use_cases = NonOfficialBookUseCases(
        BASE_URL, FakeHttpClient({empty_url: ""}), _list_factory, _details_factory
    )
    error_use_cases = NonOfficialBookUseCases(
        BASE_URL,
        FakeHttpClient({error_url: "<html>"}),
        _list_factory,
        cast(Callable[[str], BookDetailsFinderBase], details_finder_with_numero_error),
    )

    # Act
    actual = asyncio.run(empty_use_cases.fetch_book(empty_url))

    # Assert
    expected = None
    assert actual is expected
    actual = asyncio.run(error_use_cases.fetch_book(error_url))

    expected = None
    assert actual is expected


def test_fetch_book_allows_negative_numero_and_missing_image():

    # Arrange
    url = f"{BASE_URL}negative.html"
    use_cases = NonOfficialBookUseCases(
        BASE_URL,
        FakeHttpClient({url: "negative no-image"}),
        _list_factory,
        _details_factory,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_book(url))

    # Assert
    expected = None
    assert actual is not expected
    assert actual is not None
    expected = -1
    assert actual.numero == expected
    expected = ""
    assert actual.imageSourceUrl == expected
    expected = b""
    assert actual.imageContent == expected
