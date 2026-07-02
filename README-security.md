# Kubernetes Security

This document describes the Kubernetes security model used by the LSBA manifests.

## Scope

The current security model applies to the batch workloads:

- `lsba-find-books-job`
- `lsba-find-books-cronjob`
- `lsba-find-prices-job`
- `lsba-find-prices-cronjob`

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

- Kubernetes Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Kubernetes Pod Security Admission: https://kubernetes.io/docs/concepts/security/pod-security-admission/

## Kubernetes API Access

The workloads use the `lsba-sa-no-access` ServiceAccount.

The ServiceAccount disables automatic token mounting:

```yaml
automountServiceAccountToken: false
```

No `Role`, `ClusterRole`, `RoleBinding`, or `ClusterRoleBinding` is created for this ServiceAccount. The application workloads therefore do not receive Kubernetes API permissions from these manifests.

Reference:

- ServiceAccount token automount opt-out: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#opt-out-of-api-credential-automounting

## Pod Security Context

The batch Pods run as non-root users and groups:

| Environment | runAsUser | runAsGroup | fsGroup |
| --- | ---: | ---: | ---: |
| dev | `4001` | `4000` | `4000` |
| stg | `4101` | `4100` | `4100` |
| prod | `4201` | `4200` | `4200` |

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

`fsGroup` is used so mounted volumes that support Kubernetes ownership management can be read and written by the application group.

Reference:

- Kubernetes security context: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/

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

The application mounts two subdirectories from the project volume:

| Mount path | subPath | Intended writer |
| --- | --- | --- |
| `/app/data` | `data` | batch application group |
| `/app/logs` | `logs` | batch application group |

The intended Linux group ownership is:

| Environment | Group ID | Group name |
| --- | ---: | --- |
| dev | `4000` | `lsba-dev-app` |
| stg | `4100` | `lsba-stg-app` |
| prod | `4200` | `lsba-prod-app` |

PostgreSQL data is expected to use a separate data group:

| Environment | Group ID | Group name |
| --- | ---: | --- |
| dev | `4001` | `lsba-dev-data` |
| stg | `4101` | `lsba-stg-data` |
| prod | `4201` | `lsba-prod-data` |

When using local volumes, the host directories must be prepared with compatible Linux ownership and permissions. When using a cloud storage provider, the CSI driver and the Pod `fsGroup` behavior should be validated for the selected storage class.

## Verification

Render each environment and verify the security settings in the generated manifests:

```bash
kustomize build k8s/overlays/dev
kustomize build k8s/overlays/stg
kustomize build k8s/overlays/prod
```

Expected checks:

- namespaces include the Pod Security Admission labels;
- workloads use `lsba-sa-no-access-<env>`;
- ServiceAccounts have `automountServiceAccountToken: false`;
- Pods define `runAsNonRoot`, `runAsUser`, `runAsGroup`, `fsGroup`, and `seccompProfile`;
- containers define `allowPrivilegeEscalation: false` and `capabilities.drop: [ALL]`;
- no RBAC object grants Kubernetes API permissions to the workload ServiceAccount.
