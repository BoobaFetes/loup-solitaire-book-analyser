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
    finder = BiblioAventurierBookDetailsFinder(HTML)

    assert finder.isbn("default") == "9782070643027"
    assert finder.numero() == 1
    assert finder.title("default") == "Les Maîtres des Ténèbres"
    assert finder.authors() == ["Joe Dever", "Gary Chalk"]
    assert finder.lastParutionDate("1900-01-01") == "1984-07-15"
    assert finder.description("default") == "Une aventure épique."
    assert finder.official() is False
    assert finder.is_classic_version() is True
