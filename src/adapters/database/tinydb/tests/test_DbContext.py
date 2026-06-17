import asyncio

from adapters.database.tinydb.DbContext import DbContext


def test_tables_are_available_and_context_methods_are_noop(tmp_path):
    async def scenario():
        context = DbContext(str(tmp_path))
        async with context as current:
            current.books.insert({"id": 1})
            current.prices.insert({"isbn": "isbn"})
            return len(current.books), len(current.prices)

    assert asyncio.run(scenario()) == (1, 1)
