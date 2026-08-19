from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeLogger(SpyStubFake):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def stub_info(self, returned: None = None) -> None:
        self._stub("info", returned)

    @property
    def spy_info(self) -> list[SpyCall]:
        return self._spy("info")

    def info(self, message: str) -> None:
        self.messages.append(message)
        returned = self._returned_or_default("info", None)
        return self._record_call("info", (message,), {}, returned)
