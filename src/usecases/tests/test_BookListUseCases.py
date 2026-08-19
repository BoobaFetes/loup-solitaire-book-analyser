import asyncio

from domain import Book
from adapters.database.tests.fake import FakeUnitOfWork
from adapters.http.tests.fake import FakeHttpClient
from adapters.os.tests.fake import FakeFileSystem
from usecases import Assets
from usecases.BookListUseCases import BookListUseCases
from usecases.book.tests.fake import (
    FakeNonOfficialBookUseCases,
    FakeOfficialBookUseCases,
)


def make_book(
    numero: int,
    titre: str,
    isbn: str,
    *,
    official: bool,
    url: str = "",
    image_url: str = "",
) -> Book:
    return Book(
        id=numero,
        url=url or f"https://example.test/{isbn}",
        isbn=isbn,
        numero=numero,
        titre=titre,
        authors=["Joe Dever"],
        official=official,
        imageSourceUrl=image_url or f"https://images.test/{isbn}.jpg",
        imageContent=f"image-{numero}-{official}".encode("utf-8"),
    )


def test_fetch_books_merges_sources_fixes_first_title_sorts_and_persists():

    # Arrange
    official_books = [
        make_book(2, "La Traversee infernale", "9782075123181", official=True),
        make_book(1, "Les Maitres des tenebres", "9782075168694", official=True),
    ]
    non_official_books = [
        make_book(1, "Les Maîtres des Ténèbres", "9782075168694", official=False),
        make_book(
            25,
            "Sur la Piste du Loup",
            "2070519031",
            official=False,
            url="https://www.bibliotheque-des-aventuriers.com/serie/loup_solitaire/25_piste_loup.htm",
        ),
    ]
    unit_of_work = FakeUnitOfWork()
    fs = FakeFileSystem()
    assets = Assets(fs)
    use_cases = BookListUseCases(
        unit_of_work,
        FakeHttpClient(),
        FakeOfficialBookUseCases(official_books),
        FakeNonOfficialBookUseCases(non_official_books),
        assets,
    )

    # Act
    actual = asyncio.run(use_cases.fetch_books())

    # Assert
    assert [book.numero for book in actual] == [1, 2, 25]
    assert actual[0].titre == "Les Maîtres des Ténèbres"
    assert actual[-1].isbn == "2070519031"
    assert actual[-1].official is False
    assert all(book.image.startswith("assets/book-covers/") for book in actual)
    assert all(book.imageContent == b"" for book in actual)
    actual_asset_count = len(fs.files)

    expected = 3
    assert actual_asset_count == expected
    assert unit_of_work.book_repository.upserted_items == actual
