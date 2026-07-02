# TODO LIST

1. change l'infra pour acceuillir un postgres (bitnami/postgresql) (codesource et k8s avec networkpolicy)
1. ajouter un CD avec github actions pour builder les artifacts, les stocker sur github packages et les déployer sur un cluster k8s
1. voir pour faire tourner ce code sur un cloud (prod)
1. refaire les overlay de kustomize pour le cloud (prod)
1. modifier les manifests k8s afin d'utiliser un securityContext.runAsNonRoot: true et un securityContext.runAsUser: 1000
