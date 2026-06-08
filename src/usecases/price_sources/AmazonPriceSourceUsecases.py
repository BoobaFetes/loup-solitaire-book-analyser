import asyncio

from domain import Book, BookPrice
from ports import BrowserInterface
from ports.BrowserHandlers.types import TBrowser, TElement, TPage
from usecases.price_sources.AmazonPriceSourceDetails import AmazonPriceSourceDetails
from usecases.price_sources.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class AmazonPriceSourceUsecases(PriceSourceUsecasesBase):
    async def fetch_bookprices(
        self, books: list[Book], browser: BrowserInterface[TBrowser, TPage, TElement]
    ) -> list[BookPrice]:
        results: list[BookPrice] = []

        self._logger.info(f"searching book prices for {len(books)} books")
        for i in range(0, len(books), self._parallel_calls):
            selected_books = books[i : i + self._parallel_calls]

            results.extend(
                [
                    book_price
                    for book_price in await asyncio.gather(
                        *[
                            self.fetch_bookprice(book, browser)
                            for book in selected_books
                        ]
                    )
                    if book_price
                ]
            )

        return results

    async def fetch_bookprice(
        self, book: Book, browser: BrowserInterface[TBrowser, TPage, TElement]
    ) -> BookPrice | None:
        page = await browser.new_page(self.url_base)

        # search for the book using the isbn
        # await page.action.wait_for("#twotabsearchtextbox")
        await page.action.set_value("#twotabsearchtextbox", book.isbn)
        await page.action.click("#nav-search-submit-button")

        # waiting for the search results to load and display the results
        book_element = await page.action.get_by_text(book.titre)
        await page.action.wait_element(book_element)

        html = await page.html()
        close_page_action = page.close()

        details = AmazonPriceSourceDetails(html)
        price, currency = details.price_and_currency(book.isbn)
        url = details.url(self.url_base, book.isbn)

        await asyncio.gather(close_page_action)
        return BookPrice(
            isbn=book.isbn,
            source=self.url_base,
            prix=price,
            url=url,
            currency=currency,
        )
