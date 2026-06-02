import logging


class HttpxLogHandler(logging.Handler):
    __is_setup_done = False

    @classmethod
    def setup(cls, owner: str, **kwargs):
        if cls.__is_setup_done:
            return

        # Configure logging for httpx requests.
        httpx_logger = logging.getLogger("httpx")
        httpx_logger.addHandler(HttpxLogHandler(owner, **kwargs))
        httpx_logger.propagate = False  # Prevent propagation to the root logger
        cls.__is_setup_done = True

    def __init__(self, owner: str, **kwargs):
        super().__init__(**kwargs)
        self.__logger_name = owner

    def emit(self, record: logging.LogRecord) -> None:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 5:
            logger = logging.getLogger(self.__logger_name)
            record.msg = f"[{args[0]}] [{args[3]}] {args[4]} - {args[2]} - {args[1]}"
            record.args = ()  # Clear args to prevent httpx from trying to format the message
            logger.info(record.getMessage())
