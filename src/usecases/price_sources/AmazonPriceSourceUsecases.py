import asyncio

from domain import BookPrice
from ports import HttpClientBase
from usecases.price_sources.AmazonPriceSourceDetails import AmazonPriceSourceDetails
from usecases.price_sources.PriceSourceUsecasesBase import PriceSourceUsecasesBase


class AmazonPriceSourceUsecases(PriceSourceUsecasesBase):
    def _build_search_url_by_isbn(self, isbn: str) -> str:
        return f"{self.url_base}s?k={isbn}"

    async def fetch_bookprices(
        self, isbns: list[str], client: HttpClientBase
    ) -> list[BookPrice]:
        results: list[BookPrice] = []

        self._logger.info(f"Fetching book prices for {len(isbns)} ISBNs")
        for i in range(0, len(isbns), self._parallel_calls):
            selected_isbns = isbns[i : i + self._parallel_calls]
            tasks = [self.fetch_bookprice(isbn, client) for isbn in selected_isbns]
            results.extend(
                [
                    book_price
                    for book_price in await asyncio.gather(*tasks)
                    if book_price
                ]
            )

        return results

    async def fetch_bookprice(
        self, isbn: str, client: HttpClientBase
    ) -> BookPrice | None:
        url = self._build_search_url_by_isbn(isbn)
        html = await client.get_text(url)
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
