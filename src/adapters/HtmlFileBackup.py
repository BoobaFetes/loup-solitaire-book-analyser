from collections.abc import Callable


class HtmlFileBackup:
    __html_file_counter: int = 0

    def __init__(self, logger):
        import os
        from pathlib import Path

        self._logger = logger
        self.directory = Path(os.getcwd()) / "logs/html"
        self.directory.mkdir(exist_ok=True)

    async def save(
        self,
        *,
        filename_pattern: Callable[[int], str],
        log_message: Callable[[str], str | None],
        html: str,
    ) -> None:
        HtmlFileBackup.__html_file_counter += 1
        filename = filename_pattern(HtmlFileBackup.__html_file_counter)

        path = f"./logs/html/{filename}.html"
        msg = log_message(path)
        if msg:
            self._logger.info(msg)

        file = self.directory / f"{filename}.html"
        with file.open("w", encoding="utf-8") as f:
            f.write(html)
