import asyncio
from pathlib import Path

from adapters.usecase.gallimard.GallimardBookDetailsFinder import (
    GallimardBookDetailsFinder,
)
from adapters.usecase.gallimard.GallimardBookListFinder import GallimardBookListFinder
from adapters.usecase.gallimard.GallimardPriceDetailsFinder import (
    GallimardPriceDetailsFinder,
)
from adapters.http.tests.fake import FakeHttpClient
from usecases.book.OfficialBookUseCases import OfficialBookUseCases

DATASET = Path(__file__).parent / "dataset"
BASE_URL = "https://www.gallimard-jeunesse.fr"


def read_dataset(name: str) -> str:
    return (DATASET / name).read_text(encoding="utf-8")


def test_fetch_book_builds_official_book_from_gallimard_dataset():
    url = f"{BASE_URL}/9782075168694/les-maitres-des-tenebres.html"
    use_cases = OfficialBookUseCases(
        BASE_URL,
        FakeHttpClient({url: read_dataset("gallimard_9782075168694.html")}),
        GallimardBookListFinder,
        GallimardBookDetailsFinder,
        GallimardPriceDetailsFinder,
    )

    book = asyncio.run(use_cases.fetch_book(url))

    assert book is not None
    assert book.official is True
    assert book.isbn == "9782075168694"
    assert book.numero == 1
    assert book.titre == "Les Maîtres des tenèbres"
    assert "Joe Dever" in book.authors
    assert book.lastParutionDate == "2022-03-03"
    assert book.prices[0].price == 16.5
    assert book.prices[0].source == BASE_URL
    assert book.image == ""
    assert book.imageSourceUrl.endswith(".jpg")
    assert book.imageContent == b"fake-image"


def test_fetch_book_ignores_page_when_author_is_not_joe_dever():
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

    book = asyncio.run(use_cases.fetch_book(url))

    assert book is None


def test_fetch_book_urls_warms_gallimard_catalogue_session_before_fragment():
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

    urls = asyncio.run(use_cases._fetch_book_urls(client))
    text_headers = client.text_requests[0][1]
    json_headers = client.json_requests[0][1]

    assert urls == []
    assert client.cache_enabled is True
    assert client.text_requests[0][0] == referer
    assert text_headers is not None
    assert text_headers["Sec-Fetch-Mode"] == "navigate"
    assert client.json_requests[0][0] == fragment_url
    assert json_headers is not None
    assert json_headers["Referer"] == referer
    assert json_headers["X-Requested-With"] == "XMLHttpRequest"
