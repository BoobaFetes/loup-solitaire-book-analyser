# Rapport Clean Architecture

## Modificiatons apportées

| Qui           | Résumé des modifications | Date       | Status | Validateur   |
| ------------- | ------------------------ | ---------- | -------| ------------ |
| ChatGPT 5-5   | Création du rapport      | 2024-06-10 | Validé | Axel RG      |

## Introduction

Ce rapport fait le point sur l'architecture actuelle du projet sous l'angle Clean Architecture / ports-adapters (séparation propre de couches).

Le projet est un scraper. Cela change un peu la lecture habituelle : les sites cibles, leurs URLs et certains parcours web peuvent faire partie du métier, car le besoin consiste précisément à extraire des informations depuis ces sources. L'analyse ci-dessous reste donc pragmatique : l'objectif n'est pas d'obtenir une architecture academique, mais de garder des frontieres claires entre metier, ports et details techniques.

## Evaluation Par Couche

### Domain

Statut : `A surveiller`

Les entites `Book` et `BookPrice` representent correctement le coeur du domaine.

Le point a surveiller est la dependance actuelle a Pydantic. Ce choix est acceptable dans l'etat actuel du projet, notamment pour beneficier rapidement de validation et de valeurs par defaut. En revanche, dans une lecture Clean Architecture stricte, le domaine devrait idealement rester independant d'une bibliotheque de validation ou de serialisation.

Comme une refactorisation progressive vers SQLAlchemy / Postgres est prevue, cette dependance peut etre consideree comme une dette connue. SQLAlchemy ne remplace pas exactement Pydantic, mais la migration sera une bonne occasion de redefinir la frontiere entre entites de domaine, modeles de persistence et eventuels DTOs.

### Ports

Statut : `OK`, avec points a surveiller

Les ports exposent globalement les contrats attendus par les usecases : HTTP, browser, database, filesystem et parsers HTML.

Le port `browser` est volontairement technique et proche de l'outil actuel. C'est un choix defendable : il evite de creer une abstraction trop vague avant de connaitre un autre headless browser cible. Il faut simplement garder en tete que les usecases qui utilisent ce port restent proches de l'automatisation web.

Le port `usecase` est utile pour placer les parsers HTML derriere des interfaces. Les factories injectees permettent de creer les finders seulement quand le HTML est connu a l'execution.

### Adapters

Statut : `OK`

Les dependances externes principales sont correctement placees dans les adapters :

- BeautifulSoup pour le parsing HTML.
- HTTPX pour le client HTTP.
- Playwright pour l'automatisation navigateur.
- TinyDB et filesystem pour la persistence.
- Les parsers HTML specifiques a Gallimard, Bibliotheque des Aventuriers et Amazon.

Cette organisation respecte bien l'idee ports-adapters : les details techniques sont dans les couches externes, et les usecases consomment des contrats ou des factories.

### Usecases

Statut : `OK`, avec choix pragmatique assume

Les usecases ne dependent plus directement de BeautifulSoup, HTTPX, Playwright, TinyDB ou dependency-injector.

Les URLs de base, les sites cibles et certains parcours web restent dans les usecases. Dans un projet de scraping, ce choix est acceptable si l'equipe considere que le site a scraper fait partie du besoin metier. Si le site change, le comportement metier attendu change aussi.

Le point a surveiller n'est donc pas l'existence d'URLs dans les usecases, mais plutot l'accumulation potentielle de details de navigation, de selecteurs ou de formats de reponse. Tant que cela reste lisible et teste, ce n'est pas une violation bloquante.

### IoC Et Entrypoints

Statut : `OK`

Le conteneur IoC joue son role de composition : il assemble les adapters, les ports, les factories et les usecases.

`dependency-injector`, la configuration d'environnement et les valeurs techniques sont concentrees dans cette couche, ce qui est coherent avec l'architecture ports-adapters.

Les scripts d'entree `find_books.py` et `find_prices.py` restent responsables du demarrage, de l'appel aux usecases et de l'affichage des resultats.

## Points Corriges

Statut : `OK`

- Les parsers HTML ont ete deplaces derriere des ports et des factories.
- Les usecases creent les finders HTML au moment ou le HTML est disponible, au lieu de les injecter comme instances deja construites.
- Les anciens doublons morts dans `adapters/usecase` ont ete supprimes :
  - `DetailsHtmlFinderBase.py`
  - `PriceDetailsFinderBase.py`

## Points De Vigilance Restants

### `BiblioAventurierBookDetailsFinder.prices()`

Statut : `A corriger`

La methode retourne implicitement `None` car son corps est `...`.

Aujourd'hui ce n'est pas bloquant si le usecase non officiel ne l'appelle pas et assigne directement `prices=[]`. Mais c'est un piege : le contrat annonce `list[BookPrice]`, alors que l'execution renverrait `None`.

Recommandation : retourner explicitement `[]` ou lever `NotImplementedError`.

### `GallimardBookDetailsFinder.is_classic_version()`

Statut : `A surveiller`

La methode leve `NotImplementedError`, alors qu'elle est forcee par `BookDetailsFinderBase`.

Ce n'est pas bloquant tant que le finder Gallimard n'est jamais utilise pour detecter une version classique. Le signal architectural est plutot que le contrat `BookDetailsFinderBase` contient peut-etre une methode specifique a une source non officielle.

Recommandation : garder en l'etat si c'est stable, ou extraire plus tard une interface plus ciblee pour la classification de version.

### `BookDetailsFinderBase`

Statut : `A surveiller`

Le contrat est peut-etre un peu large. Il regroupe plusieurs responsabilites :

- extraction des details bibliographiques ;
- extraction des prix ;
- extraction d'image ;
- detection de version classique ;
- gestion de cas d'erreur comme les numeros invalides.

Ce n'est pas urgent a corriger, mais cela explique pourquoi certaines implementations ont des methodes inutiles, vides ou non appelees.

Recommandation : ne pas sur-decouper maintenant. Revoir ce contrat seulement si de nouvelles sources rendent ces methodes de plus en plus optionnelles.

## Conclusion

Statut global : `OK`

L'architecture actuelle est pragmatique et coherente pour un projet de scraping.

Il ne reste pas de violation majeure evidente du pattern ports-adapters. Les dependances externes importantes sont placees dans les adapters ou dans la couche IoC. Les usecases dependent majoritairement de ports, de factories et d'objets du domaine.

Les principaux prochains nettoyages recommandes sont limites :

- nettoyer les stubs et methodes mortes ;
- resserrer progressivement les contrats trop larges ;
- garder Pydantic dans le domaine comme dette connue pendant la migration vers SQLAlchemy / Postgres ;
- continuer a assumer explicitement que, dans ce projet, les sites cibles et certains parcours web font partie du metier du scraping.

En l'etat, la base est saine. Les prochaines ameliorations doivent rester proportionnees pour eviter l'over-engineering.
