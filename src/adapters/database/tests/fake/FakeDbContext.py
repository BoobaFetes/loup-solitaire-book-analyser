from ports.database import IDbContext


class FakeDbContext(IDbContext):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    async def __aenter__(self) -> IDbContext:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        self.calls.append(("start", None))

    async def stop(self):
        self.calls.append(("stop", None))

    async def begin_transaction(self, transaction_name: str):
        self.calls.append(("begin", transaction_name))

    async def commit_transaction(self):
        self.calls.append(("commit", None))

    async def rollback_transaction(self):
        self.calls.append(("rollback", None))
