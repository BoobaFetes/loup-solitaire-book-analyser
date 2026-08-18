import os
from datetime import date
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from persistence.sqlalchemy.entities.AuthorEntity import AuthorEntity
from persistence.sqlalchemy.entities.BookAuthorEntity import BookAuthorEntity
from persistence.sqlalchemy.entities.BookEntity import BookEntity

TEST_AUTHOR_NAME = "Auteur de test main.py"
TEST_BOOK_ISBN = "9999999999999"


def print_table(session: Session, entity: type, title: str) -> None:
    pprint(title)
    rows = session.execute(select(entity.__table__)).mappings().all()
    for row in rows:
        pprint(dict(row))
    if not rows:
        pprint([])


def cleanup_test_data(session: Session) -> None:
    pprint("SUPPRESSION DES DONNÉES DE TEST SI ELLES EXISTENT...")
    book = session.scalar(select(BookEntity).where(BookEntity.isbn == TEST_BOOK_ISBN))
    if book is not None:
        session.delete(book)

    author = session.scalar(
        select(AuthorEntity).where(AuthorEntity.name == TEST_AUTHOR_NAME)
    )
    if author is not None:
        session.delete(author)

    session.commit()

    # au cas où, on vérifie que les données de test ont bien été supprimées mais on garde l"idée que d'autre peuvent etre présente d'où cette ligne
    current_data = session.execute(select(BookEntity.__table__)).mappings().all()
    pprint("remaining book in database :")
    pprint(current_data)


def write_data_with_batch_user(shouldClean: bool) -> None:
    connection_string = os.environ["CONNECTION_STRING_BATCH"]
    engine = create_engine(connection_string)
    try:
        with Session(engine) as session:
            cleanup_test_data(session)

            pprint("ÉCRITURE AVEC DB_BATCH_USR...")
            book = BookEntity(
                url="https://example.test/book",
                isbn=TEST_BOOK_ISBN,
                numero=1,
                titre="Livre de test main.py",
                lastParutionDate=date(2026, 7, 13),
                description="Livre créé depuis main.py pour valider SQLAlchemy.",
                official=False,
                image="",
                acquired=False,
            )
            session.add(book)
            session.commit()
            print_table(session, BookEntity, "après insertion book :")

            author = AuthorEntity(name=TEST_AUTHOR_NAME)
            session.add(author)
            session.commit()
            print_table(session, AuthorEntity, "après insertion author :")

            book_author = BookAuthorEntity(
                book_id=book.id,
                author_id=author.id,
                position=0,
            )
            session.add(book_author)
            session.commit()
            print_table(session, BookAuthorEntity, "après insertion book_author :")

            if shouldClean:
                session.delete(book)
                session.commit()
                print_table(session, BookEntity, "après suppression book :")
                print_table(session, AuthorEntity, "author après suppression book :")
                print_table(
                    session,
                    BookAuthorEntity,
                    "book_author après suppression book :",
                )
    except Exception as e:
        pprint(f"erreur de connexion à la base de données : {e}")
    finally:
        engine.dispose()


def read_books_with_webapp_user() -> None:
    pprint("LECTURE DE LA TABLE BOOK AVEC DB_WEBAPP_USR...")
    connection_string = os.environ["CONNECTION_STRING_WEBAPP"]
    engine = create_engine(connection_string)
    try:
        with Session(engine) as session:
            print_table(session, BookEntity, "book lu avec db_webapp_usr :")
    except Exception as e:
        pprint(f"erreur de lecture avec db_webapp_usr : {e}")
    finally:
        engine.dispose()


def main():
    root_path = Path(os.getcwd())
    load_dotenv()

    log_file = root_path / "logs" / "test.log"
    captures_file = root_path / "captures" / "captures.png"

    pprint("le pod est lancé !")

    pprint("tentative d'ecriture dans les volumes montés...")
    with open(log_file, "w") as f:
        f.write("test d'écriture dans le volume monté: logs/test.log")
    with open(captures_file, "w") as f:
        f.write("test d'écriture dans le volume monté: captures/captures.png")
    pprint("écriture terminée !")

    pprint("suppression des fichiers de test...")
    log_file.unlink()
    captures_file.unlink()
    pprint("fichiers de test supprimés !")

    write_data_with_batch_user(shouldClean=False)
    read_books_with_webapp_user()

    pprint("le pod se termine !")


if __name__ == "__main__":
    main()
