import asyncio
from logging import getLogger

from adapters.RetryAction import RetryAction


def test_execute_returns_action_result_without_retry():

    # Arrange
    calls = {"action": 0, "failure": 0}

    async def action():
        calls["action"] += 1
        return "ok"

    async def on_failure(error: Exception):
        calls["failure"] += 1
        return f"failed: {error}"

    # Act
    actual = asyncio.run(
        RetryAction[str](getLogger("test")).execute(action, on_failure)
    )

    # Assert
    expected = "ok"
    assert actual == expected
    assert calls == {"action": 1, "failure": 0}


def test_execute_retries_then_returns_failure_result():

    # Arrange
    attempts = {"count": 0}

    async def action():
        attempts["count"] += 1
        raise RuntimeError("boom")

    async def on_failure(error: Exception):
        return str(error)

    # Act
    actual = asyncio.run(
        RetryAction[str](getLogger("test")).execute(action, on_failure, retry=2)
    )

    # Assert
    expected = "boom"
    assert actual == expected
    assert attempts["count"] == 3
