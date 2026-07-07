# TODO LIST

1. change l'infra pour acceuillir un postgres (bitnami/postgresql) (codesource et k8s avec networkpolicy)
1. ajouter un CD avec github actions pour builder les artifacts, les stocker sur github packages et les déployer sur un cluster k8s
1. changer les placeholders des scripts d'initialisation de la db : `db_batch_usr_pwd` et `db_webapp_usr_pwd` lors du déploiement sur le cluster k8s avant le `kustomize build ./k8s/overlays/{{ env }} | kubectl apply -f -`
1. changer le password de `db_migration_usr` qui se trouve dans le secret `userPasswordKey` de `lsba-secret-postgresql-credentials` après le déploiement
1. voir pour faire tourner ce code sur un cloud (prod)
1. refaire les overlay de kustomize pour le cloud (prod)
1. modifier les manifests k8s afin d'utiliser un securityContext.runAsNonRoot: true et un securityContext.runAsUser: 1000
