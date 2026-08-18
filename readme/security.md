# Kubernetes Security

This document describes the Kubernetes security model used by the LSBA manifests.

## Scope

The current security model applies to the batch workloads.

Common workloads deployed by all overlays:

- `lsba-find-books-cronjob`
- `lsba-find-prices-cronjob`

Local `dev`-only one-shot workloads:

- `lsba-find-books-job`
- `lsba-find-prices-job`

Storage implementation details are environment-specific and should be handled by overlays.

For local hosting, `k8s/overlays/dev` deliberately contains:

- a local `PersistentVolume` backed by `hostPath` at `/mnt/lsba/dev`;
- a `StorageClass` patch that uses `kubernetes.io/no-provisioner`.

`stg` and `prod` must use a cloud storage provider and CSI driver once the target platform is selected.

## Pod Security Standards

Namespaces enforce the Kubernetes Pod Security Standards with:

```yaml
pod-security.kubernetes.io/enforce: baseline
pod-security.kubernetes.io/audit: restricted
pod-security.kubernetes.io/warn: restricted
```

The intended policy is:

- `baseline` is enforced so Kubernetes blocks broadly unsafe pod settings.
- `restricted` is used for warnings and audit so the manifests can progressively move toward stronger hardening.

References:

- Kubernetes Pod Security Standards: <https://kubernetes.io/docs/concepts/security/pod-security-standards/>
- Kubernetes Pod Security Admission: <https://kubernetes.io/docs/concepts/security/pod-security-admission/>

## Kubernetes API Access

### `lsba-sa-no-access` ServiceAccount

The workloads use the `lsba-sa-no-access` ServiceAccount.

The ServiceAccount disables automatic token mounting:

```yaml
automountServiceAccountToken: false
```

No `Role`, `ClusterRole`, `RoleBinding`, or `ClusterRoleBinding` is created for this ServiceAccount. The application workloads therefore do not receive Kubernetes API permissions from these manifests.

Reference:

- ServiceAccount token automount opt-out: <https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#opt-out-of-api-credential-automounting>

## User and Group IDs

### Introduction

The groups are 4x0y: where x is the environment (dev, staging, prod) and y is the type of application (app or data).

**environment value (x) is:**

- 0 for dev
- 1 for staging
- 2 for prod

**each group type (y) is:**

- 1 for applications like cronjobs, jobs or webapps
- 2 for data like postgresql

### Values

| env | group id | group name | description |
| --- | -------- | ---------- | ----------- |
| dev | `4001` | **lsba-dev-app** | apps only (like jobs or webapp) |
| dev | `4002` | **lsba-dev-data** | data only (like postgresql) |
| stg | `4101` | **lsba-stg-app** | apps only (like jobs or webapp) |
| stg | `4102` | **lsba-stg-data** | data only (like postgresql) |
| prod | `4201` | **lsba-prod-app** | apps only (like jobs or webapp) |
| prod | `4202` | **lsba-prod-data** | data only (like postgresql) |

The users are for linux permissions :

| env | user id | user name | group id |
| --- | ------- | --------- | -------- |
| dev | `4000` | **lsba-dev-usr** | `4001` and `4002` |
| stg | `4100` | **lsba-stg-usr** | `4101` and `4102` |
| prod | `4200` | **lsba-prod-usr** | `4201` and `4202` |

> In K8s manifests, we use user id to do not use root (runAsNonRoot need a runAsUser), but only the group id is used for permission in the linux file system.
> WHY are user not set in linux ?
> Because, in local, we use en image of linux with docker-desktop, and the linux kernel checks the group id not the user id so we don't need to define them on the linux accounts /etc/passwd nor addUser

In local node (with desktop-docker or minikube):

- `root` (only for local and to check files in physical volumes)

    ```cmd
    k get node # to find the name of the worker node
    docker exec -it <worker_node_name> bash
    # then check the files in the physical volumes and their permissions
    root@<worker_node_name>:/# ls -l /mnt/lsba/**/**/
    ```

> we have to use root to check the files in the physical volumes, so we have to add a user for root
>
## Pod Security Context

The Pods run as non-root users and groups:
> see below for the user and group ids used in each environment.

Each Pod defines:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: <env batch user id>
  runAsGroup: <env app group id>
  fsGroup: <env app group id>
  seccompProfile:
    type: RuntimeDefault
```

so each overlays as to set the correct user and group ids for each app type like :

### apps (like batch, job or website)

| property | value |
| -------- | ----- |
| runAsUser | `4x00` |
| runAsGroup | `4x01` |
| fsGroup | `4x01` |

### database (like postgresql)

| property | value |
| -------- | ----- |
| runAsUser | `4x00` |
| runAsGroup | `4x02` |
| fsGroup | `4x02` |

`fsGroup` is used so mounted volumes that support Kubernetes ownership management can be read and written by the application group.

Reference:

- Kubernetes security context: <https://kubernetes.io/docs/tasks/configure-pod-container/security-context/>

## Container Security Context

Application containers disable privilege escalation and drop all Linux capabilities:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

The `wait-for-find-books-ends` initContainer used by `lsba-find-prices-job` follows the same rule. It also inherits the Pod-level `seccompProfile: RuntimeDefault`.

## Volume Permissions

> When using local volumes, the host directories must be prepared with compatible Linux ownership and permissions.

> When using a cloud storage provider, the CSI driver and the Pod `fsGroup` behavior should be validated for the selected storage class.

The application mounts three subdirectories from the project volume:

| Mount path | subPath | Group Ids | Intended writer |
| --- | --- | --- | --- |
| `/app/assets` | `assets` | `4x01` | for applications images or other static assets |
| `/app/logs` | `logs` | `4x01` | for applications logs |
| `/app/postgresql` | `postgresql` | `4x02` | for postgresql only |

## Verification

Render each environment and verify the security settings in the generated manifests:

```bash
kustomize build ./k8s/overlays/dev
kustomize build ./k8s/overlays/stg
kustomize build ./k8s/overlays/prod
```

Expected checks:

- namespaces include the Pod Security Admission labels;
- workloads use `lsba-sa-no-access-<env>`;
- ServiceAccounts have `automountServiceAccountToken: false`;
- Pods define `runAsNonRoot`, `runAsUser`, `runAsGroup`, `fsGroup`, and `seccompProfile`;
- containers define `allowPrivilegeEscalation: false` and `capabilities.drop: [ALL]`;
- no RBAC object grants Kubernetes API permissions to the workload ServiceAccount.
