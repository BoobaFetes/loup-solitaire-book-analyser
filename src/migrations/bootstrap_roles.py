import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def main() -> None:
    load_dotenv()
    connection_string = os.environ["CONNECTION_STRING_ADMIN"]
    script_path = Path(__file__).resolve().parent / "init-permissions.sql"
    script = script_path.read_text(encoding="utf-8")

    engine = create_engine(connection_string)
    try:
        with engine.begin() as connection:
            connection.execute(text(script))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
