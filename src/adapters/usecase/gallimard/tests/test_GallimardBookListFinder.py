from adapters.usecase.gallimard.GallimardBookListFinder import GallimardBookListFinder


def test_urls_extracts_book_item_links():

    # Arrange
    html = '<p class="BookItem-title"><a href="/catalogue/livre">Livre</a></p>'

    # Act
    actual = GallimardBookListFinder(html).urls("https://gallimard.test")

    # Assert
    expected = ["https://gallimard.test/catalogue/livre"]
    assert actual == expected
