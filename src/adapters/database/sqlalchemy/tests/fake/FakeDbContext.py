from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeDbContext(SpyStubFake):
    def __init__(self) -> None:
        super().__init__()

    @property
    def spy_operation_session(self) -> list[SpyCall]:
        return self._spy("operation_session")

    def operation_session(self):
        error = RuntimeError("database unavailable")
        self._record_call("operation_session", (), {}, error)
        raise error
