from collections.abc import Awaitable, Callable
from logging import Logger
from typing import Generic, TypeVar

TExecuteResult = TypeVar("TExecuteResult")


class RetryAction(Generic[TExecuteResult]):
    def __init__(self, logger: Logger):
        self.__logger = logger

    async def execute(
        self,
        action: Callable[[], Awaitable[TExecuteResult]],
        on_failure: Callable[[Exception], Awaitable[TExecuteResult]],
        retry_message: Callable[[int], str] | None = None,
        use_error_log: bool = True,
        retry: int = 3,
    ) -> TExecuteResult:
        if not retry_message:
            retry_message = lambda r: f"Action failed. Retrying... ({r} retries left)"  # noqa: E731

        try:
            return await action()
        except Exception as e:
            if retry > 0:
                self.__logger.warning(retry_message(retry))
                return await self.execute(
                    action,
                    on_failure=on_failure,
                    retry_message=retry_message,
                    use_error_log=use_error_log,
                    retry=retry - 1,
                )

            if use_error_log:
                self.__logger.error(f"Action failed after retries: {e}", exc_info=True)

            return await on_failure(e)
