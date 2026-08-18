# Command Reminder

Useful local commands:

| command | usage |
| --- | --- |
| `& ./scripts/reload-infra.ps1` | Recreate the local `dev` infrastructure, build `k8s/overlays/dev-build.yaml`, apply it, then port-forward PostgreSQL. |
| `& ./scripts/reload-infra.ps1 -Clean` | Delete the local `dev` Kubernetes resources and clean local node folders without recreating them. |
| `& ./scripts/serve-local-database.ps1` | Port-forward PostgreSQL on `localhost:5432`. |
| `& ./scripts/new-docker-image.ps1` | Build the local Docker image with the default image name and tag. |
| `& ./scripts/new-docker-image.ps1 -image <name> -tag <tag>` | Build a local Docker image with a custom name and tag. |
| `kustomize build ./k8s/overlays/dev/ --enable-helm > ./k8s/overlays/dev-build.yaml` | Generate the local development manifest file. |
| `k apply -f ./k8s/overlays/dev-build.yaml` | Apply the generated local development manifests. |
| `k delete -f ./k8s/overlays/dev-build.yaml` | Delete the generated local development manifests from the cluster. |
