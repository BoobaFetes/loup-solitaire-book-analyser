import re

from adapters.usecase.amazon.AmazonPriceDetailsFinder import AmazonPriceDetailsFinder


HTML = """
<div role="listitem">
  <div data-cy="title-recipe">
    <a href="/Livre-Loup?keywords=9780000000001"><h2>Le Labyrinthe de la Mort</h2></a>
  </div>
  <div data-cy="price-recipe"><span class="a-price"><span>12,50 €</span></span></div>
</div>
"""


def test_url_returns_matching_details_url():
    finder = AmazonPriceDetailsFinder(HTML)

    assert finder.url(isbn="9780000000001", base_url="https://amazon.test") == (
        "https://amazon.test/Livre-Loup?keywords=9780000000001"
    )


def test_price_and_currency_returns_price_for_matching_title():
    finder = AmazonPriceDetailsFinder(HTML)

    assert finder.price_and_currency(
        isbn="9780000000001",
        title_pattern=re.compile("Labyrinthe"),
    ) == (12.5, "€")


def test_url_requires_isbn_and_base_url():
    finder = AmazonPriceDetailsFinder("")

    for kwargs in [{}, {"isbn": "9780000000001"}]:
        try:
            finder.url(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError was not raised")
