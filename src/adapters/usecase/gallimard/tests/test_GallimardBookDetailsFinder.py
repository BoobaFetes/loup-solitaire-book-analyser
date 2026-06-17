from adapters.usecase.gallimard.GallimardBookDetailsFinder import GallimardBookDetailsFinder


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
    finder = GallimardBookDetailsFinder(HTML)

    assert finder.isbn("default") == "9782070643027"
    assert finder.numero() == 1
    assert finder.title("default") == "Les Maîtres des Ténèbres"
    assert finder.authors() == ["Joe Dever", "Gary Chalk"]
    assert finder.description("default") == "Une aventure épique."
    assert finder.official() is True

    prices = finder.prices(isbn="9782070643027", url="https://gallimard.test/livre")
    assert len(prices) == 1
    assert prices[0].source == "Gallimard Jeunesse"
    assert prices[0].price == 14.9


def test_prices_requires_isbn_and_url():
    finder = GallimardBookDetailsFinder("")

    for kwargs in [{}, {"isbn": "9782070643027"}]:
        try:
            finder.prices(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")
