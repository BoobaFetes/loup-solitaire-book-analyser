import asyncio

from domain import Book, BookPrice
from ports import BrowserInterface
from ports.BrowserHandlers.types import TBrowser, TElement, TPage
from usecases.price_sources.AmazonPriceSourceDetails import AmazonPriceSourceDetails
from usecases.price_sources.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class AmazonPriceSourceUsecases(PriceSourceUsecasesBase):
    async def fetch_bookprices(
        self,
        books: list[Book],
        browser: BrowserInterface[TBrowser, TPage, TElement],
        context_index: int = 0,
    ) -> list[BookPrice]:
        results: list[BookPrice] = []

        self._logger.info(f"searching book prices for {len(books)} books")
        for book in books:
            self._logger.info(
                f"searching book price for n°{book.numero} {book.titre} ({book.isbn})"
            )
            price = await self.fetch_bookprice(book, browser, context_index)
            if price and price.prix > 0:
                results.append(price)

        return results

    async def fetch_bookprice(
        self,
        book: Book,
        browser: BrowserInterface[TBrowser, TPage, TElement],
        context_index: int = 0,
    ) -> BookPrice | None:
        page = await browser.new_page(self.url_base, context_index)

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
