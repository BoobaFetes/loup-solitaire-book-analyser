import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-batch-usr-pwd", default="db_batch_usr_pwd")
    parser.add_argument("--db-webapp-usr-pwd", default="db_webapp_usr_pwd")
    return parser.parse_args()


def postgres_string_literal(value: str) -> str:
    return value.replace("'", "''")


def main() -> None:
    load_dotenv()
    args = parse_args()
    connection_string = os.environ["CONNECTION_STRING_ADMIN"]
    script_path = Path(__file__).resolve().parent / "init-permissions.sql"
    script = script_path.read_text(encoding="utf-8")
    script = script.replace(
        "db_batch_usr_pwd", postgres_string_literal(args.db_batch_usr_pwd)
    )
    script = script.replace(
        "db_webapp_usr_pwd", postgres_string_literal(args.db_webapp_usr_pwd)
    )

    engine = create_engine(connection_string)
    try:
        with engine.begin() as connection:
            connection.execute(text(script))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
