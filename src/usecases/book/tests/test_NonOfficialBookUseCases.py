import asyncio
from pathlib import Path

from adapters.usecase.biblio_aventurier.BiblioAventurierBookDetailsFinder import (
    BiblioAventurierBookDetailsFinder,
)
from adapters.usecase.biblio_aventurier.BiblioAventurierBookListFinder import (
    BiblioAventurierBookListFinder,
)
from ports.http import HttpClientBase
from usecases.book.NonOfficialBookUseCases import NonOfficialBookUseCases

DATASET = Path(__file__).parent / "dataset"
BASE_URL = "https://www.bibliotheque-des-aventuriers.com/"


def read_dataset(name: str) -> str:
    return (DATASET / name).read_text(encoding="utf-8", errors="replace")


class FakeHttpClient(HttpClientBase[object, object]):
    def __init__(self, texts: dict[str, str] | None = None) -> None:
        self.texts = texts or {}
        self.content_requests: list[str] = []
        self.opened = False

    async def open(self, **kwargs) -> None:
        self.opened = True

    async def close(self) -> None:
        self.opened = False

    async def get_text(
        self, endpoint: str, encoding: str | None = None, retry: int = 3
    ) -> str:
        return self.texts.get(endpoint, "")

    async def get_content(self, endpoint: str, retry: int = 3) -> bytes:
        self.content_requests.append(endpoint)
        return b"fake-image"


def make_use_cases(client: FakeHttpClient) -> NonOfficialBookUseCases:
    return NonOfficialBookUseCases(
        BASE_URL,
        client,
        BiblioAventurierBookListFinder,
        BiblioAventurierBookDetailsFinder,
    )


def test_fetch_book_builds_non_official_book_from_biblio_dataset():
    url = f"{BASE_URL}serie/loup_solitaire/02_traversee_infernale.htm"
    use_cases = make_use_cases(
        FakeHttpClient({url: read_dataset("biblio_aventurier_9782075123181.html")})
    )

    book = asyncio.run(use_cases.fetch_book(url))

    assert book is not None
    assert book.official is False
    assert book.isbn == "9782075123181"
    assert book.numero == 2
    assert book.titre == "La Traversée Infernale"
    assert "Joe Dever" in book.authors
    assert book.image


def test_fetch_book_ignores_classic_version():
    url = f"{BASE_URL}serie/loup_solitaire/01_maitres_tenebres_classique.htm"
    use_cases = make_use_cases(
        FakeHttpClient(
            {url: read_dataset("biblio_aventurier_fake_maitres_tenebres_classique.html")}
        )
    )

    book = asyncio.run(use_cases.fetch_book(url))

    assert book is None


def test_fetch_book_accepts_augmented_version():
    url = f"{BASE_URL}serie/loup_solitaire/01_maitres_tenebres_augmentee.htm"
    use_cases = make_use_cases(
        FakeHttpClient({url: read_dataset("biblio_aventurier_9782075168694.html")})
    )

    book = asyncio.run(use_cases.fetch_book(url))

    assert book is not None
    assert book.isbn == "9782075168694"
    assert book.numero == 1
    assert book.titre == "Les Maîtres des Ténèbres"


def test_fetch_book_accepts_book_missing_from_gallimard_source():
    url = f"{BASE_URL}serie/loup_solitaire/25_piste_loup.htm"
    use_cases = make_use_cases(
        FakeHttpClient({url: read_dataset("biblio_aventurier_2070519031.html")})
    )

    book = asyncio.run(use_cases.fetch_book(url))

    assert book is not None
    assert book.isbn == "2070519031"
    assert book.numero == 25
    assert book.titre == "Sur la Piste du Loup"
    assert book.url == url
    assert book.official is False
