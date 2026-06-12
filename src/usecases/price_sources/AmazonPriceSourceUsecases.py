import asyncio
import re

from domain import Book, BookPrice
from ports import BrowserInterface
from ports.BrowserHandlers.types import TBrowser, TElement, TPage
from usecases.price_sources.AmazonPriceSourceDetails import AmazonPriceSourceDetails
from usecases.price_sources.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class AmazonPriceSourceUsecases(PriceSourceUsecasesBase):
    @staticmethod
    def __title_pattern(title: str) -> re.Pattern[str]:
        apostrophes = "'’‘ʼ`´"
        pattern = "".join(
            r"\s+"
            if char.isspace()
            else f"[{re.escape(apostrophes)}]"
            if char in apostrophes
            else re.escape(char)
            for char in title
        )
        return re.compile(pattern, re.IGNORECASE)

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
            if price and price.price > 0:
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
        await page.action.wait_for("#twotabsearchtextbox", state="visible")

        await page.action.set_value("#twotabsearchtextbox", book.isbn)
        await page.action.click("#nav-search-submit-button")

        # waiting for the search results to load and display the expected book
        if not await page.action.wait_for(
            'div[role="listitem"] div[data-cy="title-recipe"] h2',
            state="visible",
            has_text=self.__title_pattern(book.titre),
        ):
            self._logger.info(
                f"Book n°{book.numero} {book.titre} ({book.isbn}) not found on Amazon"
            )
            await page.close()
            return None

        html = await page.html()
        close_page_action = page.close()

        details = AmazonPriceSourceDetails(html)
        price, currency = details.price_and_currency(book.isbn)
        url = details.url(self.url_base, book.isbn)

        await asyncio.gather(close_page_action)
        return BookPrice(
            isbn=book.isbn,
            source=self.url_base,
            price=price,
            currency=currency,
            url=url,
        )
