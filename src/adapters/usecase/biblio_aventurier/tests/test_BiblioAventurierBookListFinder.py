from adapters.usecase.biblio_aventurier.BiblioAventurierBookListFinder import (
    BiblioAventurierBookListFinder,
)


def test_urls_extracts_book_links():

    # Arrange
    html = """
    <body><table><tr><td>
      <table></table>
      <table><tr><td></td><td><table><tr><td>
        <p></p><p></p><p></p><p></p><p></p><p></p><p></p><p></p>
        <p><a href="../livres/01.html">Livre</a></p>
      </td></tr></table></td></tr></table>
    </td></tr></table></body>
    """

    # Act
    actual = BiblioAventurierBookListFinder(html).urls("https://biblio.test/")

    # Assert
    expected = ["https://biblio.test/livres/01.html"]
    assert actual == expected
