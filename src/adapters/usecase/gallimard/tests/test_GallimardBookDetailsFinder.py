from adapters.usecase.gallimard.GallimardBookDetailsFinder import (
    GallimardBookDetailsFinder,
)


HTML = """
<h1 class="Book-title">Les Maîtres des Ténèbres</h1>
<p class="Book-suptitle">Loup Solitaire - 1</p>
<div class="Book-contributors"><p><a>Joe
Dever</a><a>Gary Chalk</a></p></div>
<div class="Book-resume">Une aventure épique.</div>
<div class="Book-cover"><img src="https://img.test/cover.jpg" /></div>
<ul>
  <li class="Book-detailsSet"><p></p><p><strong>9782070643027</strong></p><p><strong>15/07/1984</strong></p></li>
</ul>
<p class="Book-price"><span>Prix</span><span>14,90 €</span></p>
"""


def test_extracts_book_details_and_price_from_html():

    # Arrange
    finder = GallimardBookDetailsFinder(HTML)

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
    actual = finder.description("default")

    expected = "Une aventure épique."
    assert actual == expected
    assert finder.official() is True

    actual = finder.prices(isbn="9782070643027", url="https://gallimard.test/livre")

    expected = 1
    assert len(actual) == expected
    assert actual[0].source == "Gallimard Jeunesse"
    assert actual[0].price == 14.9


def test_prices_requires_isbn_and_url():

    # Arrange
    finder = GallimardBookDetailsFinder("")

    # Act
    for kwargs in [{}, {"isbn": "9782070643027"}]:
        try:
            finder.prices(**kwargs)
        except ValueError:
            # Assert
            pass
        else:
            raise AssertionError("ValueError was not raised")
