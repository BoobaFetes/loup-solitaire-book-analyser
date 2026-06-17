from adapters.usecase.gallimard.GallimardBookListFinder import GallimardBookListFinder


def test_urls_extracts_book_item_links():
    html = '<p class="BookItem-title"><a href="/catalogue/livre">Livre</a></p>'

    assert GallimardBookListFinder(html).urls("https://gallimard.test") == [
        "https://gallimard.test/catalogue/livre"
    ]
