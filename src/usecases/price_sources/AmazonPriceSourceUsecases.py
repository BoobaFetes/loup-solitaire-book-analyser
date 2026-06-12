import asyncio
import re

from domain import Book, BookPrice
from ports import BrowserInterface
from ports.BrowserHandlers.types import TBrowser, TElement, TPage
from usecases.price_sources.AmazonPriceSourceDetails import AmazonPriceSourceDetails
from usecases.price_sources.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class AmazonPriceSourceUsecases(PriceSourceUsecasesBase):
    def __init__(
        self,
        url_base: str,
        parallel_calls: int = 5,
        request_delay_seconds: float = 1.0,
    ):
        super().__init__(url_base, parallel_calls)
        self.__request_delay_seconds = request_delay_seconds

    @staticmethod
    def __normalize_title_by_regexp_pattern(title: str) -> re.Pattern[str]:
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
        for index, book in enumerate(books):
            if index > 0 and self.__request_delay_seconds > 0:
                await asyncio.sleep(self.__request_delay_seconds)

            self._logger.info(
                f"searching book price for n°{book.numero} {book.titre} ({book.isbn})"
            )
            price = await self.fetch_bookprice(book, browser, context_index)
            if price:
                results.append(price)

        return results

    async def fetch_bookprice(
        self,
        book: Book,
        browser: BrowserInterface[TBrowser, TPage, TElement],
        context_index: int = 0,
    ) -> BookPrice | None:
        page = await browser.new_page(self.url_base, context_index)
        self._logger.info("Amazon home loaded: %s", await page.current_url())

        # search for the book using the isbn
        await page.action.wait_for("#twotabsearchtextbox", state="visible")

        previous_url = await page.current_url()
        await page.action.set_value("#twotabsearchtextbox", book.isbn)
        await page.action.click("#nav-search-submit-button")
        await page.wait_for_url_change(previous_url)
        self._logger.info(
            "Amazon search page loaded for ISBN %s: %s",
            book.isbn,
            await page.current_url(),
        )

        # waiting for the search results to load and display the expected book
        if not await page.action.wait_for(
            'div[role="listitem"] div[data-cy="title-recipe"] h2',
            state="visible",
            has_text=self.__normalize_title_by_regexp_pattern(book.titre),
        ):
            self._logger.info(
                f"Book n°{book.numero} {book.titre} ({book.isbn}) not found on Amazon"
            )
            await page.close()
            return None

        html = await page.html()
        close_page_action = page.close()

        details = AmazonPriceSourceDetails(html)
        price, currency = details.price_and_currency(
            self.__normalize_title_by_regexp_pattern(book.titre),
            book.isbn,
        )
        url = details.url(self.url_base, book.isbn)

        await asyncio.gather(close_page_action)
        return BookPrice(
            isbn=book.isbn,
            source=self.url_base,
            price=price,
            currency=currency,
            url=url,
        )
