import asyncio
from typing import cast

from adapters.database.file_system.Database import Database
from adapters.database.file_system.DbContext import DbContext


class FakeDatabase:
    def __init__(self):
        self.calls: list[str] = []

    async def start(self):
        self.calls.append("start")

    async def stop(self):
        self.calls.append("stop")


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
