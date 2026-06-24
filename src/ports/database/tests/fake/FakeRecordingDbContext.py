from ports.database import IDbContext


class FakeRecordingDbContext(IDbContext):
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    async def __aenter__(self) -> IDbContext:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()

    async def start(self) -> None:
        self.calls.append(("start", None))

    async def stop(self) -> None:
        self.calls.append(("stop", None))

    async def begin_transaction(self, transaction_name: str) -> None:
        self.calls.append(("begin", transaction_name))

    async def commit_transaction(self) -> None:
        self.calls.append(("commit", None))

    async def rollback_transaction(self) -> None:
        self.calls.append(("rollback", None))
