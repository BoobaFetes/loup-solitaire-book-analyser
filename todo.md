# TODO LIST

1. [EN COURS] changer l'infra pour acceuillir un postgres (bitnami/postgresql) (codesource et k8s avec networkpolicy)
    1. ouvrir la conversation du 10/07/2026 avec codex: Créer connexion base de données
    1. demande à l'ia de verifi que la doc et le CI et CD soient cohérents - on ne veut pas de doc fausse
    1. vérifier que la nouvelle stratégie fonctione au niveau infra
        - kusto build
        - connection à la base de données depuis dbeaver
    1. passer au code pour implementer un simple appel à la base (main est dejà fait pour donc faut jsute que ca passe sans exception)
    1. implementer alembic pour pouvoir effectuer les migrations (creation de la db)
    1. implementer l'unit of work des adapters sqlalchemy
    1. revoir les tests unitaires de l'ensemble de l'applications (sont compliquer .....)
    1. lancer les job pour verifier qu'en base tout est persisté et que le runtime est OK
    1. valider la PR use-postgres et add-postgres
1. changer le password de `db_migration_usr` qui se trouve dans le secret `userPasswordKey` de `lsba-secret-postgresql-credentials` après le déploiement
    - toujours d'actualité ? (normalement non car une stratégie de livraison a clairement ete établie et documentée)
1. changer les placeholders des scripts d'initialisation de la db : `db_batch_usr_pwd` et `db_webapp_usr_pwd` lors du déploiement sur le cluster k8s avant le `kustomize build ./k8s/overlays/{{ env }} | kubectl apply -f -`
    - ne devrait plus être nécessaire car la stratégie de livraison a été établie et documentée  => utilisation d'un secret k8s pour stocker les passwords et d'une commande pour mettre à jour les passeworks d'user applicatifs
1. voir pour faire tourner ce code sur un cloud (prod)
1. ajouter un CD avec github actions pour builder les artifacts, les stocker sur github packages et les déployer sur un cluster k8s
    - attention un CD est apparu pour aide-mémoire sur la stratgie mise en place (notameent la rotation des passwords)
1. refaire les overlay de kustomize pour le cloud (prod)
1. modifier les manifests k8s afin d'utiliser un securityContext.runAsNonRoot: true et un securityContext.runAsUser: 1000
