import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from persistence.sqlalchemy.entities.DbProbeEntity import DbProbeEntity


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
        with Session(engine) as session:
            probe = DbProbeEntity(message="test de connexion depuis main.py")
            session.add(probe)
            session.commit()

            count = session.scalar(select(func.count()).select_from(DbProbeEntity))
            print(
                "connexion base de données OK : "
                f"db_probe id={probe.id}, total={count}"
            )
    except Exception as e:
        print(f"erreur de connexion à la base de données : {e}")
    finally:
        engine.dispose()

    print("le pod se termine !")


if __name__ == "__main__":
    main()
