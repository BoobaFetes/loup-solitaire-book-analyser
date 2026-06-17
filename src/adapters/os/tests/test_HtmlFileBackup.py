import asyncio
import os
from logging import getLogger

from adapters.os.HtmlFileBackup import HtmlFileBackup


def test_save_writes_html_file_and_logs_message(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    backup = HtmlFileBackup(getLogger("backup-test"))

    with caplog.at_level("INFO", logger="backup-test"):
        asyncio.run(
            backup.save(
                filename_pattern=lambda counter: f"page_{counter}",
                log_message=lambda path: f"saved {path}",
                html="<html>ok</html>",
            )
        )

    files = list((tmp_path / "logs" / "html").glob("page_*.html"))
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8") == "<html>ok</html>"
    assert any("saved ./logs/html/page_" in message for message in caplog.messages)
    assert os.getcwd() == str(tmp_path)
