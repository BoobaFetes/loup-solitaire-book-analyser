import asyncio
from typing import cast

from adapters.database.file_system.Database import Database
from adapters.database.file_system.DbContext import DbContext
from adapters.database.file_system.tests.fake import FakeDatabase


def test_start_stop_and_context_manager_delegate_to_database():
    async def scenario():
        db = FakeDatabase()
        context = DbContext(cast(Database, db))
        await context.start()
        await context.stop()
        async with context:
            pass
        return db.calls

    assert asyncio.run(scenario()) == ["start", "stop", "start", "stop"]
