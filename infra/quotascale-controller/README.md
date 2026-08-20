# QuotaScale Controller KPT Package

This package installs the
[SSU-DCN QuotaScale Controller](https://github.com/SSU-DCN/quotascale-controller)
and its `QuotaAutoscaler` and `NodeScalingInventory` CRDs.

## Default behavior

- Namespace: `quotascale-controller`
- Quota check interval: `10s`
- Minimum delay between quota updates: `10s`
- Node scaling: enabled
- Node-scaling repository: `http://13.212.192.49:32100/nephio/workload-cluster.git`
- Node scale-in delay: `10s`
- Scale-in exempt namespaces: `longhorn-system,metallb-system`
- Prepared/activated spare nodes: `2` / `1`
- Forced node scale-in: disabled

The controller manages CPU and memory values on existing `ResourceQuota`
objects. Create `QuotaAutoscaler` resources separately in each workload
namespace that should be managed.

## Container image

The package uses the public Linux AMD64 image
`jangwonlee/quotascale-controller:latest` from Docker Hub. Override the
`image-quotascale-controller` setter when a different registry or immutable
version tag is required.

## Setters

| Setter | Default | Description |
| --- | --- | --- |
| `namespace` | `quotascale-controller` | Controller namespace |
| `image-quotascale-controller` | `jangwonlee/quotascale-controller:latest` | Controller image |
| `image-pull-policy` | `Always` | Always pull the mutable `latest` image |
| `image-revision` | `b0b1602` | Rollout marker for the controller image revision |
| `quota-check-interval-arg` | `--quota-check-interval=10s` | Periodic utilization check |
| `quota-update-interval-arg` | `--quota-update-interval=10s` | Per-namespace resize rate limit |
| `enable-node-scaling-arg` | `--enable-node-scaling=true` | Enable the node-scaling controller |
| `node-scaling-repo-url-arg` | `--node-scaling-repo-url=http://13.212.192.49:32100/nephio/workload-cluster.git` | GitOps repository containing the target MachineDeployment |
| `node-scale-in-delay-arg` | `--node-scale-in-delay=10s` | Delay before node scale-in |
| `node-scale-in-exempt-namespaces-arg` | `--node-scale-in-exempt-namespaces=longhorn-system,metallb-system` | Namespaces excluded from scale-in eviction checks |
| `node-scaling-prepared-spares-arg` | `--node-scaling-prepared-spares=2` | Desired prepared spare nodes |
| `node-scaling-activated-spares-arg` | `--node-scaling-activated-spares=1` | Desired activated spare nodes |
| `enable-node-scale-in-force-arg` | `--enable-node-scale-in-force=false` | Disable forced scale-in |
| `gitops-secret-name` | `quotascale-git-credentials` | Secret containing Git username and password |
| `cpu-request` | `200m` | Controller CPU request |
| `memory-request` | `2Gi` | Controller memory request |
| `cpu-limit` | `2` | Controller CPU limit |
| `memory-limit` | `2Gi` | Controller memory limit |

## Render and inspect

```bash
kpt fn render infra/quotascale-controller
kpt live init infra/quotascale-controller
kpt live apply infra/quotascale-controller --dry-run
```

## Node scaling

Node scaling requires a writable Git repository containing the target CAPI
`MachineDeployment`, plus repository credentials. Before applying the package,
create the credentials Secret in the controller namespace:

```bash
kubectl -n quotascale-controller create secret generic quotascale-git-credentials \
  --from-literal=username=nephio \
  --from-literal=password='<GIT_PASSWORD>'
```

The Deployment maps these keys to the upstream controller's `GITEA_USERNAME`
and `GITEA_PASSWORD` environment variables. The password is deliberately not a
KPT setter because this package is stored in a public repository. If the
`namespace` or `gitops-secret-name` setter is changed, create the Secret using
the same values.
