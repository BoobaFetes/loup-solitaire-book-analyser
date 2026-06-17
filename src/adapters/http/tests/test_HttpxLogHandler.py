import logging

from adapters.http.HttpxLogHandler import HttpxLogHandler


def test_emit_reformats_httpx_access_log_record(caplog):
    handler = HttpxLogHandler("owner")
    record = logging.LogRecord(
        "httpx",
        logging.INFO,
        "test.py",
        1,
        "%s %s %s %s %s",
        ("GET", "https://example.test", "HTTP/1.1", 200, "OK"),
        None,
    )

    with caplog.at_level(logging.INFO, logger="owner"):
        handler.emit(record)

    assert "[GET] [200] OK - HTTP/1.1 - https://example.test" in caplog.messages
