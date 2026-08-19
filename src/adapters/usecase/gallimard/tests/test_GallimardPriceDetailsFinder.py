from adapters.usecase.gallimard.GallimardPriceDetailsFinder import (
    GallimardPriceDetailsFinder,
)


def test_price_and_currency_extracts_price():

    # Arrange
    html = '<p class="Book-price"><span>Prix</span><span>14,90 €</span></p>'

    # Act
    actual = GallimardPriceDetailsFinder(html).price_and_currency()

    # Assert
    expected = (14.9, "€")
    assert actual == expected


def test_price_and_currency_returns_default_when_price_is_missing():

    # Arrange
    finder = GallimardPriceDetailsFinder("")

    # Act
    actual = finder.price_and_currency()

    # Assert
    expected = (0.0, "not set")
    assert actual == expected
