import asyncio
import logging

from ioc import new_ioc_container, print_environment_variables

# load dependencies
container = new_ioc_container()

logger = logging.getLogger(__name__)
logger.info("IOC container initialized")

print_environment_variables(container, logger)

# arrange
book_list = container.book_list_usecases()
book_prices = container.book_price_usecases()


# action
async def main():
    logger.info("Starting find prices process")
    pre_books = await book_list.list()
    await book_prices.fetch_prices(pre_books)
    books = await book_prices.bind_prices_to_books(pre_books)

    logger.info("")
    logger.info("summary:")
    sorted_book = sorted(books, key=lambda b: b.numero)
    for book in sorted_book:
        logger.info(f" - {book.numero} - {book.titre}:")
        for price in book.prices:
            logger.info(f"   - {price}")

    logger.info("Finished find prices process")


if __name__ == "__main__":
    asyncio.run(main())
