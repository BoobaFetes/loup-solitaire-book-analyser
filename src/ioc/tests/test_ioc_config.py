from dependency_injector import providers

from ioc.IocContainer import IocContainer, convert_env_variables_as


def test_convert_env_variables_as_bool_from_string(monkeypatch):
    config = providers.Configuration()

    monkeypatch.setenv("HEADLESS", "true")

    value = convert_env_variables_as(
        wanted_type=bool,
        config=config.headless,
        name="HEADLESS",
        default=False,
    )

    assert value is True
    assert config.headless() is True


def test_convert_env_variables_as_bool_from_default_bool(monkeypatch):
    config = providers.Configuration()

    monkeypatch.delenv("HEADLESS", raising=False)

    value = convert_env_variables_as(
        wanted_type=bool,
        config=config.headless,
        name="HEADLESS",
        default=True,
    )

    assert value is True
    assert config.headless() is True


def test_convert_env_variables_as_numeric_values(monkeypatch):
    config = providers.Configuration()

    monkeypatch.setenv("API_PARALLEL_CALLS", "2")
    monkeypatch.setenv("AMAZON_REQUEST_DELAY_SECONDS", "1.5")

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

    assert parallel_calls == 2
    assert config.api_parallel_calls() == 2
    assert delay == 1.5
    assert config.amazon_request_delay_seconds() == 1.5


def test_http_client_headers_resolve_configuration_options():
    container = IocContainer()
    container.config.api_timeout.from_value(0.5)
    container.config.browser_user_agent.from_value("Mozilla/5.0 test")
    container.config.browser_accept_language.from_value("fr-FR")

    client = container.http_client()

    assert client.client_options["headers"] == {
        "User-Agent": "Mozilla/5.0 test",
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "fr-FR",
    }
    assert client.client_options["follow_redirects"] is True
