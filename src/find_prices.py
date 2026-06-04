import asyncio
import logging

from ioc import new_ioc_container, print_environment_variables

# load dependencies
container = new_ioc_container()

logger = logging.getLogger(__name__)
logger.info("IOC container initialized")

print_environment_variables(container, logger)

logger.info("IOC : common instances (singleton) created")

# arrange
book_list = container.book_list_usecases()
book_prices = container.book_price_usecases()


# action
async def main():
    logger.info("Starting find prices process")
    books = await book_list.list()
    books_with_prices = book_prices.bind_prices_to_books(
        books, await book_prices.fetch_prices(books)
    )

    logger.info("")
    logger.info("summary:")
    sorted_book = sorted(books_with_prices, key=lambda b: b.numero)
    for book in sorted_book:
        logger.info(f" - {book.numero} - {book.titre}:")
        for price in book.prices:
            logger.info(f"   - {price}")

    logger.info("Finished find prices process")


asyncio.run(main())
