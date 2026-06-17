from adapters.usecase.gallimard.GallimardPriceDetailsFinder import GallimardPriceDetailsFinder


def test_price_and_currency_extracts_price():
    html = '<p class="Book-price"><span>Prix</span><span>14,90 €</span></p>'

    assert GallimardPriceDetailsFinder(html).price_and_currency() == (14.9, "€")


def test_price_and_currency_returns_default_when_price_is_missing():
    assert GallimardPriceDetailsFinder("").price_and_currency() == (0.0, "not set")
