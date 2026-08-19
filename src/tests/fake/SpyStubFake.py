from dataclasses import dataclass
from typing import Any


_MISSING = object()


@dataclass(frozen=True)
class SpyCall:
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    returned: Any


class SpyStubFake:
    def __init__(self) -> None:
        self._stubbed_returns: dict[str, Any] = {}
        self._stubbed_exceptions: dict[str, BaseException] = {}
        self._spy_calls: dict[str, list[SpyCall]] = {}

    def _stub(self, method_name: str, returned: Any) -> None:
        self._stubbed_returns[method_name] = returned

    def _stub_exception(self, method_name: str, exception: BaseException) -> None:
        self._stubbed_exceptions[method_name] = exception

    def _returned_or_default(self, method_name: str, default: Any) -> Any:
        returned = self._stubbed_returns.get(method_name, _MISSING)
        return default if returned is _MISSING else returned

    def _raise_if_stubbed_exception(self, method_name: str) -> None:
        exception = self._stubbed_exceptions.get(method_name)
        if exception is not None:
            raise exception

    def _record_call(
        self,
        method_name: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        returned: Any,
    ) -> Any:
        self._spy_calls.setdefault(method_name, []).append(
            SpyCall(args=args, kwargs=dict(kwargs), returned=returned)
        )
        return returned

    def _spy(self, method_name: str) -> list[SpyCall]:
        return self._spy_calls.get(method_name, [])
