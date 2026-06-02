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
book_usecases = container.book_usecases()


# action
async def main():
    logger.info("Starting find prices process")
    text = """
    books = await book_usecases.fetch_prices()
    logger.info(f"Found {len(books)} books")

    for book in books:
        logger.info(f"Finding prices for book: {book.title}")
        await book_usecases.fetch_prices(book)

    """
    logger.info(text)
    logger.info("Finished find prices process")


asyncio.run(main())
