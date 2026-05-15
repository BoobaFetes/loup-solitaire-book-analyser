from ..domain.entities.tome import Tome


def afficher_tome_console(tome: Tome):
    tome.afficher_info()


def afficher_liste_console(tomes):
    for t in tomes:
        afficher_tome_console(t)
