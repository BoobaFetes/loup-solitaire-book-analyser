# TODO LIST

1. ajouter un CI/CD avec github actions pour generer un build
1. modifier le CI/CD pour qu'il se déclenche à chaque push sur la branche main
1. modifier le CI/CD pour qu'il pousse le build sur dockerhub ou tout autre registry de container
1. DONE - SUR K8S LOCAL - récuperer le build depuis dockerhub et le faire tourner en local
1. refaire les overlay de kustomize pour le local (dev)
1. générer les tests unitaires et l'environnement de test
1. voir pour faire tourner ce code sur un cloud (prod)
1. refaire les overlay de kustomize pour le cloud (prod)
1. modifier les manifests k8s afin d'utiliser un securityContext.runAsNonRoot: true et un securityContext.runAsUser: 1000
