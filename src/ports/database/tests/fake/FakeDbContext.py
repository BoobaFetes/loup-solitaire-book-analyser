from ports.database import IDbContext


class FakeDbContext(IDbContext):
    async def __aenter__(self) -> IDbContext:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def start(self):
        pass

    async def stop(self):
        pass

    async def begin_transaction(self, transaction_name: str):
        pass

    async def commit_transaction(self):
        pass

    async def rollback_transaction(self):
        pass
