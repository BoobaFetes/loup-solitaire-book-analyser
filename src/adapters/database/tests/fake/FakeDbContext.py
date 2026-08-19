from ports.database import IDbContext
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeDbContext(IDbContext, SpyStubFake):
    def __init__(self) -> None:
        SpyStubFake.__init__(self)
        self.calls: list[tuple[str, None]] = []

    def stub_start(self, returned: None = None) -> None:
        self._stub("start", returned)

    @property
    def spy_start(self) -> list[SpyCall]:
        return self._spy("start")

    def stub_stop(self, returned: None = None) -> None:
        self._stub("stop", returned)

    @property
    def spy_stop(self) -> list[SpyCall]:
        return self._spy("stop")

    def stub_begin_transaction(self, returned: None = None) -> None:
        self._stub("begin_transaction", returned)

    @property
    def spy_begin_transaction(self) -> list[SpyCall]:
        return self._spy("begin_transaction")

    def stub_commit_transaction(self, returned: None = None) -> None:
        self._stub("commit_transaction", returned)

    @property
    def spy_commit_transaction(self) -> list[SpyCall]:
        return self._spy("commit_transaction")

    def stub_rollback_transaction(self, returned: None = None) -> None:
        self._stub("rollback_transaction", returned)

    @property
    def spy_rollback_transaction(self) -> list[SpyCall]:
        return self._spy("rollback_transaction")

    async def __aenter__(self) -> IDbContext:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def start(self):
        self.calls.append(("start", None))
        returned = self._returned_or_default("start", None)
        return self._record_call("start", (), {}, returned)

    async def stop(self):
        self.calls.append(("stop", None))
        returned = self._returned_or_default("stop", None)
        return self._record_call("stop", (), {}, returned)

    async def begin_transaction(self):
        self.calls.append(("begin", None))
        returned = self._returned_or_default("begin_transaction", None)
        return self._record_call("begin_transaction", (), {}, returned)

    async def commit_transaction(self):
        self.calls.append(("commit", None))
        returned = self._returned_or_default("commit_transaction", None)
        return self._record_call("commit_transaction", (), {}, returned)

    async def rollback_transaction(self):
        self.calls.append(("rollback", None))
        returned = self._returned_or_default("rollback_transaction", None)
        return self._record_call("rollback_transaction", (), {}, returned)
