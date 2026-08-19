from adapters.usecase.biblio_aventurier.BiblioAventurierBookDetailsFinder import (
    BiblioAventurierBookDetailsFinder,
)


HTML = """
<table id="AutoNumber1">
  <p>Les Maîtres des Ténèbres (classique)</p>
  <a href="../../images/couverture.jpg">image</a>
</table>
<table id="AutoNumber2">
  <tr><td></td><td></td></tr>
  <tr><td></td><td>
    <font>
      <a>Loup Solitaire n° 1</a>
      <a>Joe Dever</a>
      <a>Gary Chalk</a>
      <i>Flight from the Dark</i>
      15 juillet 1984
    </font>
    <p><span>ISBN 978-2-07-064302-7</span></p>
  </td></tr>
  <tr><td><p></p><p></p><p></p><p></p><p>Une aventure épique.</p></td></tr>
</table>
"""


def test_extracts_book_details_from_html():

    # Arrange
    finder = BiblioAventurierBookDetailsFinder(HTML)

    # Act
    actual = finder.isbn("default")

    # Assert
    expected = "9782070643027"
    assert actual == expected
    assert finder.numero() == 1
    actual = finder.title("default")

    expected = "Les Maîtres des Ténèbres"
    assert actual == expected
    assert finder.authors() == ["Joe Dever", "Gary Chalk"]
    actual = finder.lastParutionDate("1900-01-01")

    expected = "1984-07-15"
    assert actual == expected
    actual = finder.description("default")

    expected = "Une aventure épique."
    assert actual == expected
    assert finder.official() is False
    assert finder.is_classic_version() is True
