import asyncio
from logging import getLogger

from adapters.RetryAction import RetryAction


def test_execute_returns_action_result_without_retry():
    calls = {"action": 0, "failure": 0}

    async def action():
        calls["action"] += 1
        return "ok"

    async def on_failure(error: Exception):
        calls["failure"] += 1
        return f"failed: {error}"

    result = asyncio.run(RetryAction[str](getLogger("test")).execute(action, on_failure))

    assert result == "ok"
    assert calls == {"action": 1, "failure": 0}


def test_execute_retries_then_returns_failure_result():
    attempts = {"count": 0}

    async def action():
        attempts["count"] += 1
        raise RuntimeError("boom")

    async def on_failure(error: Exception):
        return str(error)

    result = asyncio.run(
        RetryAction[str](getLogger("test")).execute(action, on_failure, retry=2)
    )

    assert result == "boom"
    assert attempts["count"] == 3
