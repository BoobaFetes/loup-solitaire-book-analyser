# DOBNE LIST

1. merger les données liés aux livres afin de ne concerver que ceux de la liste officiel en premier et si un livre n'a pas été réédité récupérer ses données depuis le site de référence des fans
1. scrapper les sites sélectionnés pour récupérer les prix de chaque livres via leur ISBN
1. scraper les sites selectionnés pour récuperer la liste des livbres et leur détail
1. exécution de l'application python dans un cluster K8S
1. les cronjob et job charge les données dans la db posgres
1. un postgresql à l'écoute sur le port 5432 et protégé par network policy
1. proteger les connection string dans des secrets K8S (pour le moment)
1. protéger les pods de mauvaise pratique et les isoler de la couche bar-metal 

# TODO LIST

1. voir pour faire tourner ce code sur un cloud (prod)
1. ajouter un CD avec github actions pour builder les artifacts, les stocker sur github packages et les déployer sur un cluster k8s
    - attention un CD est apparu pour aide-mémoire sur la stratgie mise en place (notameent la rotation des passwords)
1. refaire les overlay de kustomize pour le cloud (prod)
