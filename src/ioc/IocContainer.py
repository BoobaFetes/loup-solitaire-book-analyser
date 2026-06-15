import os
from collections.abc import Callable
from logging import Handler, Logger, StreamHandler, basicConfig, handlers
from pathlib import Path
from typing import TypeVar, cast

from dependency_injector import containers, providers

from adapters import (
    BookFileRepository,
    BookPriceFileRepository,
    BrowserAdapter,
    FileSystemAdapter,
    HttpClientAdapter,
)
from adapters.browser.PageHandlerAdapter import PageHandlerAdapter
from usecases import BookListUseCases, BookPriceUseCases
from usecases.book_list.NonOfficialBookUseCases import NonOfficialBookUseCases
from usecases.book_list.OfficialBookUseCases import OfficialBookUseCases
from usecases.price_sources import AmazonPriceSourceUsecases

DEFAULT_BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"


def _make_logging_handlers(root_dir: str, log_file: str) -> list[Handler]:
    log_path = (Path(root_dir) / log_file).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return [
        # permet de faire une rotation des logs tous les jours à minuit et conservation des 31 derniers jours de log
        handlers.TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",  # Rotate at midnight
            interval=1,  # Rotate daily
            backupCount=31,  # Keep 31 days of logs
        ),
        # garde aussi les logs console pour faciliter le développement et le debug ou voir directement dans k8s
        StreamHandler(),
    ]


class IocContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # region resources

    logging = providers.Resource(
        basicConfig,
        level=config.log_level,
        format="{asctime} [ {levelname:^8} ] [{taskName!s:^8}] [{name:^24}] {message}",
        style="{",
        handlers=providers.Factory(
            _make_logging_handlers,
            root_dir=config.root_dir,
            log_file=config.log_file,
        ),
    )

    # endregion

    # region adapters (ports implementation)

    http_client = providers.Singleton(
        HttpClientAdapter,
        retry_delay=config.api_timeout,
        headers=providers.Dict({"User-Agent": config.browser_user_agent}),
    )

    file_system = providers.Singleton(
        FileSystemAdapter,
        path=config.root_dir,
    )
    book_price_repository = providers.Singleton(
        BookPriceFileRepository,
        fs=file_system,
        connection_string=config.connection_string,
    )
    book_repository = providers.Singleton(
        BookFileRepository,
        fs=file_system,
        connection_string=config.connection_string,
        price_repository=book_price_repository,
    )
    # endregion

    # region usecases

    # region book_list usecases

    official_book_usecases = providers.Singleton(
        OfficialBookUseCases,
        repository=book_repository,
        client=http_client,
        parallel_calls=config.api_parallel_calls,
    )

    non_official_book_usecases = providers.Singleton(
        NonOfficialBookUseCases,
        repository=book_repository,
        client=http_client,
        parallel_calls=config.api_parallel_calls,
    )

    # endregion

    # region book price usecases
    browser = providers.Singleton(
        BrowserAdapter,
        page_factory=lambda page: PageHandlerAdapter(page),
        headless=config.headless,
        args=[
            "--disable-dev-shm-usage",
        ],
        browser_context_options=providers.Dict(
            user_agent=config.browser_user_agent,
            viewport=providers.Dict(
                width=config.browser_viewport_width,
                height=config.browser_viewport_height,
            ),
            locale=config.browser_locale,
            timezone_id=config.browser_timezone,
            extra_http_headers=providers.Dict(
                {"Accept-Language": config.browser_accept_language}
            ),
            java_script_enabled=True,
        ),
    )

    amazon_price_source_usecases = providers.Singleton(
        AmazonPriceSourceUsecases,
        url_base="https://www.amazon.fr/",
        parallel_calls=config.api_parallel_calls,
        request_delay_seconds=config.amazon_request_delay_seconds,
    )

    # endregion

    book_list_usecases = providers.Singleton(
        BookListUseCases,
        repository=book_repository,
        client=http_client,
        official_book=official_book_usecases,
        non_official_book=non_official_book_usecases,
    )

    book_price_usecases = providers.Singleton(
        BookPriceUseCases,
        repository=book_price_repository,
        browser=browser,
        sources=providers.List(
            amazon_price_source_usecases,
        ),
    )

    # endregion


TConvertedType = TypeVar("TConvertedType", int, float, bool)


def convert_env_variables_as(
    wanted_type: type[TConvertedType],
    config: providers.ConfigurationOption,
    name: str,
    default: TConvertedType | None = None,
    required: bool = False,
) -> TConvertedType | None:
    config.from_env(name, default=default, required=required)
    value = config()
    converted_value = (
        cast(
            TConvertedType,
            value if isinstance(value, bool) else value.lower() in ("true", "1"),
        )
        if wanted_type is bool
        else wanted_type(value)
    )
    config.from_value(converted_value)
    return converted_value


def convert_env_variables_as_path(
    config: providers.ConfigurationOption,
    name: str,
    value_fn: Callable[[Path], str],
    required: bool = False,
    default: str | None = None,
) -> str:
    config.from_env(name, default=default, required=required)
    value = config()
    file = Path(value)
    converted_value = value_fn(file)
    config.from_value(converted_value)
    return converted_value


def new_ioc_container(script_name: str) -> IocContainer:
    container = IocContainer()

    # load environment variables
    container.config.env.from_env("ENV", default="dev")
    if container.config.env() == "dev":
        # charge les variables du fichier .env si l'environnement est dev car pour tout autre environnement ces variables sont fourni via l'environnement d'exécution (ex: docker, kubernetes, etc...)
        from dotenv import load_dotenv

        load_dotenv()

    # bind configuration values
    container.config.root_dir.from_env("ROOT_DIR", default=os.getcwd())
    container.config.connection_string.from_env("CONNECTION_STRING", required=True)
    container.config.log_level.from_env("LOG_LEVEL", default="INFO")

    convert_env_variables_as(
        wanted_type=bool,
        config=container.config.headless,
        name="HEADLESS",
        default=False,
    )
    container.config.browser_user_agent.from_env(
        "BROWSER_USER_AGENT",
        default=DEFAULT_BROWSER_USER_AGENT,
    )
    convert_env_variables_as(
        wanted_type=int,
        config=container.config.browser_viewport_width,
        name="BROWSER_VIEWPORT_WIDTH",
        default=1920,
    )
    convert_env_variables_as(
        wanted_type=int,
        config=container.config.browser_viewport_height,
        name="BROWSER_VIEWPORT_HEIGHT",
        default=1080,
    )
    container.config.browser_locale.from_env("BROWSER_LOCALE", default="fr-FR")
    container.config.browser_timezone.from_env(
        "BROWSER_TIMEZONE",
        default="Europe/Paris",
    )
    container.config.browser_accept_language.from_env(
        "BROWSER_ACCEPT_LANGUAGE",
        default="fr-FR,fr;q=0.9,en;q=0.8",
    )
    convert_env_variables_as(
        wanted_type=float,
        config=container.config.amazon_request_delay_seconds,
        name="AMAZON_REQUEST_DELAY_SECONDS",
        default=1.0,
    )

    # arrange log file name to include script name for better separation of logs between different scripts
    convert_env_variables_as_path(
        config=container.config.log_file,
        name="LOG_FILE",
        required=True,
        value_fn=lambda path: str(
            path.parent / f"{path.stem}_{script_name.strip('_')}{path.suffix}"
        ),
    )

    # environment variables are strings by default, force API timeout to numeric
    convert_env_variables_as(
        wanted_type=float,
        config=container.config.api_timeout,
        name="API_TIMEOUT",
        default=0.5,
    )
    convert_env_variables_as(
        wanted_type=int,
        config=container.config.api_parallel_calls,
        name="API_PARALLEL_CALLS",
        default=2,
    )

    # check values
    root_dir = Path(container.config.root_dir())
    if root_dir.is_file():
        raise ValueError(
            "root_dir must be a directory, not a file. Value provided: " + str(root_dir)
        )
    if not root_dir.exists():
        raise ValueError(
            "root_dir must be an existing directory. Value provided: " + str(root_dir)
        )

    container.init_resources()
    return container


def print_environment_variables(container: IocContainer, logger: Logger):
    variables = [
        ("ENV", os.getenv("ENV", "dev")),
        ("ROOT_DIR", container.config.root_dir()),
        ("API_TIMEOUT", container.config.api_timeout()),
        ("API_PARALLEL_CALLS", container.config.api_parallel_calls()),
        ("CONNECTION_STRING", container.config.connection_string()),
        ("LOG_LEVEL", container.config.log_level()),
        ("LOG_FILE", container.config.log_file()),
        ("HEADLESS", container.config.headless()),
        ("BROWSER_USER_AGENT", container.config.browser_user_agent()),
        (
            "BROWSER_VIEWPORT",
            f"{container.config.browser_viewport_width()}x{container.config.browser_viewport_height()}",
        ),
        ("BROWSER_LOCALE", container.config.browser_locale()),
        ("BROWSER_TIMEZONE", container.config.browser_timezone()),
        ("BROWSER_ACCEPT_LANGUAGE", container.config.browser_accept_language()),
        (
            "AMAZON_REQUEST_DELAY_SECONDS",
            container.config.amazon_request_delay_seconds(),
        ),
    ]
    logger.info("environment variables:")
    for key, value in variables:
        logger.info(f" - {key} = {value}")
