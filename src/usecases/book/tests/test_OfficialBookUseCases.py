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
    assert book.image


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
