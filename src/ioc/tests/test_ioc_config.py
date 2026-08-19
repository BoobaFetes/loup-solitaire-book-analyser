from logging import Logger as LoggingLogger
from typing import cast

from dependency_injector import providers

from ioc.IocContainer import (
    IocContainer,
    convert_env_variables_as,
    convert_env_variables_as_path,
    new_ioc_container,
    print_environment_variables,
)
from ioc.tests.fake import FakeLogger


def test_convert_env_variables_as_bool_from_string(monkeypatch):

    # Arrange
    config = providers.Configuration()

    monkeypatch.setenv("HEADLESS", "true")

    # Act
    actual = convert_env_variables_as(
        wanted_type=bool,
        config=config.headless,
        name="HEADLESS",
        default=False,
    )

    # Assert
    expected = True
    assert actual is expected
    assert config.headless() is True


def test_convert_env_variables_as_bool_from_default_bool(monkeypatch):

    # Arrange
    config = providers.Configuration()

    monkeypatch.delenv("HEADLESS", raising=False)

    # Act
    actual = convert_env_variables_as(
        wanted_type=bool,
        config=config.headless,
        name="HEADLESS",
        default=True,
    )

    # Assert
    expected = True
    assert actual is expected
    assert config.headless() is True


def test_convert_env_variables_as_numeric_values(monkeypatch):

    # Arrange
    config = providers.Configuration()

    monkeypatch.setenv("API_PARALLEL_CALLS", "2")
    monkeypatch.setenv("AMAZON_REQUEST_DELAY_SECONDS", "1.5")

    # Act
    parallel_calls = convert_env_variables_as(
        wanted_type=int,
        config=config.api_parallel_calls,
        name="API_PARALLEL_CALLS",
        default=6,
    )
    delay = convert_env_variables_as(
        wanted_type=float,
        config=config.amazon_request_delay_seconds,
        name="AMAZON_REQUEST_DELAY_SECONDS",
        default=1.0,
    )

    # Assert
    assert parallel_calls == 2
    assert config.api_parallel_calls() == 2
    assert delay == 1.5
    assert config.amazon_request_delay_seconds() == 1.5


def test_convert_env_variables_as_path_rewrites_env_path(monkeypatch, tmp_path):

    # Arrange
    config = providers.Configuration()
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))

    # Act
    actual = convert_env_variables_as_path(
        config=config.log_file,
        name="LOG_FILE",
        value_fn=lambda path: str(path.parent / f"{path.stem}_job{path.suffix}"),
    )

    # Assert
    expected = str(tmp_path / "app_job.log")
    assert actual == expected
    assert config.log_file() == actual


def test_http_client_headers_resolve_configuration_options(tmp_path):

    # Arrange
    container = IocContainer()
    container.config.root_dir.from_value(str(tmp_path))
    container.config.api_timeout.from_value(0.5)
    container.config.browser_user_agent.from_value("Mozilla/5.0 test")
    container.config.browser_accept_language.from_value("fr-FR")
    container.config.inmemory_cache_dir.from_value("caches")
    container.config.inmemory_cache_enabled.from_value(False)

    # Act
    client = container.http_client()

    # Assert
    assert client.client_options["headers"] == {
        "User-Agent": "Mozilla/5.0 test",
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "fr-FR",
    }
    assert client.client_options["follow_redirects"] is True


def test_new_ioc_container_loads_environment_configuration(monkeypatch, tmp_path):

    # Arrange
    cache_dir = tmp_path / "caches"
    cache_dir.mkdir()
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("ROOT_DIR", str(tmp_path))
    monkeypatch.setenv("CONNECTION_STRING_BATCH", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("CONNECTION_STRING_WEBAPP", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "app.log"))
    monkeypatch.setenv("CACHE_DIR", "caches")
    monkeypatch.setenv("INMEMORY_CACHE_ENABLED", "false")
    monkeypatch.setenv("HEADLESS", "true")
    monkeypatch.setenv("BROWSER_USER_AGENT", "agent")
    monkeypatch.setenv("BROWSER_VIEWPORT_WIDTH", "800")
    monkeypatch.setenv("BROWSER_VIEWPORT_HEIGHT", "600")
    monkeypatch.setenv("BROWSER_LOCALE", "fr-FR")
    monkeypatch.setenv("BROWSER_TIMEZONE", "Europe/Paris")
    monkeypatch.setenv("BROWSER_ACCEPT_LANGUAGE", "fr-FR")
    monkeypatch.setenv("AMAZON_REQUEST_DELAY_SECONDS", "0.25")
    monkeypatch.setenv("API_TIMEOUT", "0.75")
    monkeypatch.setenv("API_PARALLEL_CALLS", "3")

    # Act
    container = new_ioc_container("find_books")

    try:
        # Assert
        assert container.config.root_dir() == str(tmp_path)
        assert container.config.log_file() == str(tmp_path / "app_find_books.log")
        assert container.config.inmemory_cache_enabled() is False
        assert container.config.headless() is True
        assert container.config.browser_viewport_width() == 800
        assert container.config.browser_viewport_height() == 600
        assert container.config.amazon_request_delay_seconds() == 0.25
        assert container.config.api_timeout() == 0.75
        assert container.config.api_parallel_calls() == 3
    finally:
        container.shutdown_resources()


def test_new_ioc_container_rejects_file_root_dir(monkeypatch, tmp_path):

    # Arrange
    root_file = tmp_path / "root.txt"
    root_file.write_text("not a dir", encoding="utf-8")
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("ROOT_DIR", str(root_file))
    monkeypatch.setenv("CONNECTION_STRING_BATCH", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("CONNECTION_STRING_WEBAPP", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "app.log"))

    # Act
    try:
        new_ioc_container("job")
    except ValueError as error:
        # Assert
        assert "must be a directory" in str(error)
    else:
        raise AssertionError("ValueError was not raised")


def test_new_ioc_container_rejects_missing_root_dir(monkeypatch, tmp_path):

    # Arrange
    missing_root = tmp_path / "missing"
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("ROOT_DIR", str(missing_root))
    monkeypatch.setenv("CONNECTION_STRING_BATCH", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("CONNECTION_STRING_WEBAPP", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "app.log"))

    # Act
    try:
        new_ioc_container("job")
    except ValueError as error:
        # Assert
        assert "must be an existing directory" in str(error)
    else:
        raise AssertionError("ValueError was not raised")


def test_print_environment_variables_logs_current_config():

    # Arrange
    container = IocContainer()
    for name, value in {
        "env": "test",
        "root_dir": "root",
        "api_timeout": 1.0,
        "api_parallel_calls": 2,
        "connection_string_batch": "batch",
        "connection_string_webapp": "webapp",
        "inmemory_cache_enabled": False,
        "log_level": "INFO",
        "log_file": "app.log",
        "headless": True,
        "browser_user_agent": "agent",
        "browser_viewport_width": 800,
        "browser_viewport_height": 600,
        "browser_locale": "fr-FR",
        "browser_timezone": "Europe/Paris",
        "browser_accept_language": "fr-FR",
        "amazon_request_delay_seconds": 0.5,
    }.items():
        getattr(container.config, name).from_value(value)
    logger = FakeLogger()

    # Act
    print_environment_variables(container, cast(LoggingLogger, logger))

    # Assert
    assert "environment variables:" in logger.messages
    assert " - ENV = test" in logger.messages
    assert " - BROWSER_VIEWPORT = 800x600" in logger.messages
