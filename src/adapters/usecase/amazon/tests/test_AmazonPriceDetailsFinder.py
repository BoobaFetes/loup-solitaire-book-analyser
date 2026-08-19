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

    # Arrange
    finder = AmazonPriceDetailsFinder(HTML)

    # Act
    actual = finder.url(isbn="9780000000001", base_url="https://amazon.test")

    # Assert
    expected = "https://amazon.test/Livre-Loup?keywords=9780000000001"
    assert actual == expected


def test_price_and_currency_returns_price_for_matching_title():

    # Arrange
    finder = AmazonPriceDetailsFinder(HTML)

    # Act
    actual = finder.price_and_currency(
        isbn="9780000000001",
        title_pattern=re.compile("Labyrinthe"),
    )

    # Assert
    expected = (12.5, "€")
    assert actual == expected


def test_url_requires_isbn_and_base_url():

    # Arrange
    finder = AmazonPriceDetailsFinder("")

    # Act
    for kwargs in [{}, {"isbn": "9780000000001"}]:
        try:
            finder.url(**kwargs)
        except ValueError:
            # Assert
            pass
        else:
            raise AssertionError("ValueError was not raised")
