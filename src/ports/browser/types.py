from typing import TypeVar

# les types doivent être invariants
# pourquoi ?
# 1. en clean architecture seul la classe concrète connait le type utilisé, et souvent cela depends de la librairie utilisée,  # 2. les coucjes uses case et domain n'ont certainement pas à connaitre les types concrets car cela ahjouterait une dépendance à une couche externe (comme un device (chromium, http, data persistence, UI avec un objet CSS)


TBrowser = TypeVar("TBrowser")  # les types sont invariants
TPage = TypeVar("TPage")  # les types sont invariants
TElement = TypeVar("TElement")  # les types sont invariants
