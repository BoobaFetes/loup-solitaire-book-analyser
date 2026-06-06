from domain import BookPrice
from ports import BrowserInterface
from ports.BrowserHandlers.types import TBrowser, TElement, TPage
from usecases.price_sources.AmazonPriceSourceDetails import AmazonPriceSourceDetails
from usecases.price_sources.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class AmazonPriceSourceUsecases(PriceSourceUsecasesBase):
    def _build_search_url_by_isbn(self, isbn: str) -> str:
        return f"{self.url_base}s?k={isbn}"

    async def fetch_bookprices(
        self, isbns: list[str], browser: BrowserInterface[TBrowser, TPage, TElement]
    ) -> list[BookPrice]:
        results: list[BookPrice] = []

        # TODO : il faut revoir le process, car si on ouvre immédiatement la page avec .?k=<isbn> on se retrouve avec un page vide avec "toutes nos excuses, l'équipe d'amazon"
        # je penses que le message est claire : l'équipe d'amazon me remercie d'avoir essayer et de faire partie de leur statistique, histoire de me verrouiller y a pas mieux .....

        self._logger.info(f"searching book prices for {len(isbns)} ISBNs")
        for i in range(0, len(isbns), self._parallel_calls):
            selected_isbns = isbns[i : i + self._parallel_calls]
            price = await self.fetch_bookprice(selected_isbns[0], browser)
            if price:
                results.append(price)
            # for debug tasks = [self.fetch_bookprice(isbn, browser) for isbn in selected_isbns]
            # for debug results.extend(
            # for debug     [
            # for debug         book_price
            # for debug         for book_price in await asyncio.gather(*tasks)
            # for debug         if book_price
            # for debug     ]
            # for debug )

        return results

    async def fetch_bookprice(
        self, isbn: str, browser: BrowserInterface[TBrowser, TPage, TElement]
    ) -> BookPrice | None:
        url = self._build_search_url_by_isbn(isbn)
        page = await browser.new_page(url)
        html = await page.html()
        if not html:
            self._logger.warning(
                f"No HTML content retrieved for ISBN {isbn} from {self.url_base}"
            )
            return None

        details = AmazonPriceSourceDetails(html)

        price, currency = details.price_and_currency(isbn)
        return BookPrice(
            isbn=isbn,
            source=self.url_base,
            prix=price,
            url=details.url(self.url_base, isbn),
            currency=currency,
        )
