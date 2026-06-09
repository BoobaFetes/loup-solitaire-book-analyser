import os
from pathlib import Path


def main():
    root_path = Path(os.getcwd())

    log_file = root_path / "logs" / "test.log"
    data_file = root_path / "data" / "test.json"

    print("le pod est lancé !")

    print("tentative d'ecriture dans les volumes montés...")
    with open(log_file, "w") as f:
        f.write("test d'écriture dans le volume monté")
    print("écriture terminée !")
    with open(data_file, "w") as f:
        f.write("test d'écriture dans le volume monté")
    print("écriture terminée !")

    print("suppression des fichiers de test...")
    log_file.unlink()
    data_file.unlink()
    print("fichiers de test supprimés !")

    print("le pod se termine !")


if __name__ == "__main__":
    main()
