import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def main():
    root_path = Path(os.getcwd())
    load_dotenv()

    log_file = root_path / "logs" / "test.log"

    print("le pod est lancé !")

    print("tentative d'ecriture dans les volumes montés...")
    with open(log_file, "w") as f:
        f.write("test d'écriture dans le volume monté")
    print("écriture terminée !")

    print("suppression des fichiers de test...")
    log_file.unlink()
    print("fichiers de test supprimés !")

    print("tentative de connexion à la base de données...")
    connection_string = os.environ["CONNECTION_STRING_BATCH"]
    engine = create_engine(connection_string)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar_one()
            print(f"connexion base de données OK : SELECT 1 = {result}")
    except Exception as e:
        print(f"erreur de connexion à la base de données : {e}")
    finally:
        engine.dispose()

    print("le pod se termine !")


if __name__ == "__main__":
    main()
