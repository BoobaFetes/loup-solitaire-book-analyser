from ports.cache import CacheStoredValue
from tests.fake.SpyStubFake import SpyCall, SpyStubFake


class FakeInMemoryCache(SpyStubFake):
    def __init__(
        self, cached_value: CacheStoredValue | None = None, enabled: bool = True
    ):
        super().__init__()
        self.cached_value = cached_value
        self.enabled = enabled
        self.get_calls = 0
        self.set_background_calls = 0
        self.flushed = False

    def stub_is_enabled(self, returned: bool) -> None:
        self._stub("is_enabled", returned)

    @property
    def spy_is_enabled(self) -> list[SpyCall]:
        return self._spy("is_enabled")

    def stub_get(self, returned: CacheStoredValue | None) -> None:
        self._stub("get", returned)

    @property
    def spy_get(self) -> list[SpyCall]:
        return self._spy("get")

    def stub_set(self, returned: None = None) -> None:
        self._stub("set", returned)

    @property
    def spy_set(self) -> list[SpyCall]:
        return self._spy("set")

    def stub_set_background(self, returned: None = None) -> None:
        self._stub("set_background", returned)

    @property
    def spy_set_background(self) -> list[SpyCall]:
        return self._spy("set_background")

    def stub_clear(self, returned: None = None) -> None:
        self._stub("clear", returned)

    @property
    def spy_clear(self) -> list[SpyCall]:
        return self._spy("clear")

    def stub_flush(self, returned: None = None) -> None:
        self._stub("flush", returned)

    @property
    def spy_flush(self) -> list[SpyCall]:
        return self._spy("flush")

    def is_enabled(self) -> bool:
        returned = self._returned_or_default("is_enabled", self.enabled)
        return self._record_call("is_enabled", (), {}, returned)

    def clear(self) -> None:
        self.cached_value = None
        returned = self._returned_or_default("clear", None)
        return self._record_call("clear", (), {}, returned)

    def get(self, key: str) -> CacheStoredValue | None:
        self.get_calls += 1
        returned = self._returned_or_default("get", self.cached_value)
        return self._record_call("get", (key,), {}, returned)

    async def set(
        self, key: str, value: CacheStoredValue, encoding: str | None = None
    ) -> None:
        self.cached_value = value
        returned = self._returned_or_default("set", None)
        return self._record_call("set", (key, value), {"encoding": encoding}, returned)

    def set_background(
        self, key: str, value: CacheStoredValue, encoding: str | None = None
    ) -> None:
        self.set_background_calls += 1
        self.cached_value = value
        returned = self._returned_or_default("set_background", None)
        return self._record_call(
            "set_background", (key, value), {"encoding": encoding}, returned
        )

    async def flush(self) -> None:
        self.flushed = True
        returned = self._returned_or_default("flush", None)
        return self._record_call("flush", (), {}, returned)
