import os
from logging import Handler, Logger, StreamHandler, basicConfig, handlers
from pathlib import Path

from dependency_injector import containers, providers

from adapters import (
    BookFileRepository,
    BookPriceFileRepository,
    BrowserAdapter,
    FileSystemAdapter,
    HttpClientAdapter,
)
from adapters.BrowserHandlers.PageHandlerAdapter import PageHandlerAdapter
from usecases import BookListUseCases, BookPriceUseCases
from usecases.book_list.NonOfficialBookUseCases import NonOfficialBookUseCases
from usecases.book_list.OfficialBookUseCases import OfficialBookUseCases
from usecases.price_sources import AmazonPriceSourceUsecases


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
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        },
    )

    file_system = providers.Singleton(
        FileSystemAdapter,
        path=config.root_dir,
    )
    book_repository = providers.Singleton(
        BookFileRepository,
        fs=file_system,
        connection_string=config.connection_string,
    )
    book_price_repository = providers.Singleton(
        BookPriceFileRepository,
        fs=file_system,
        connection_string=config.connection_string,
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
        env=config.env,
    )

    amazon_price_source_usecases = providers.Singleton(
        AmazonPriceSourceUsecases,
        url_base="https://www.amazon.fr/",
        parallel_calls=config.api_parallel_calls,
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


def check_numeric_env_variables(
    wanted_type: type, value: str, variable_name: str
) -> int | float | None:
    try:
        return wanted_type(value)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"{variable_name} must be a {wanted_type.__name__}. Value provided: {value}"
        ) from e


def new_ioc_container() -> IocContainer:
    container = IocContainer()

    # load environment variables
    container.config.env.from_env("ENV", default="dev")
    if container.config.env() == "dev":
        # charge les variables du fichier .env si l'environnement est dev car pour tout autre environnement ces variables sont fourni via l'environnement d'exécution (ex: docker, kubernetes, etc...)
        from dotenv import load_dotenv

        load_dotenv()

    # bind configuration values
    container.config.root_dir.from_env("ROOT_DIR", default=os.getcwd())
    container.config.api_timeout.from_env("API_TIMEOUT", default=0.5)
    container.config.api_parallel_calls.from_env("API_PARALLEL_CALLS", default=2)
    container.config.connection_string.from_env("CONNECTION_STRING", required=True)
    container.config.log_level.from_env("LOG_LEVEL", default="INFO")
    container.config.log_file.from_env("LOG_FILE", required=True)

    # environment variables are strings by default, force API timeout to numeric
    api_timeout = check_numeric_env_variables(
        float, container.config.api_timeout(), "API_TIMEOUT"
    )
    container.config.api_timeout.from_value(api_timeout)
    api_parallel_calls = check_numeric_env_variables(
        int, container.config.api_parallel_calls(), "API_PARALLEL_CALLS"
    )
    container.config.api_parallel_calls.from_value(api_parallel_calls)

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
        ("CONNECTION_STRING", container.config.connection_string()),
        ("LOG_LEVEL", container.config.log_level()),
        ("LOG_FILE", container.config.log_file()),
    ]
    logger.info("environment variables:")
    for key, value in variables:
        logger.info(f" - {key} = {value}")
