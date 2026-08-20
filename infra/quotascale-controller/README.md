# QuotaScale Controller KPT Package

This package installs the
[SSU-DCN QuotaScale Controller](https://github.com/SSU-DCN/quotascale-controller)
and its `QuotaAutoscaler` and `NodeScalingInventory` CRDs.

## Default behavior

- Namespace: `quotascale-controller`
- Quota check interval: `1m`
- Minimum delay between quota updates: `1m`
- Node scaling: disabled

With node scaling disabled, the controller manages CPU and memory values on
existing `ResourceQuota` objects. Create `QuotaAutoscaler` resources separately
in each workload namespace that should be managed.

## Container image requirement

The upstream project does not currently publish a public container image. The
default `image-quotascale-controller` value is the intended GHCR location, but
the image must be built and published before deployment or replaced with an
accessible image in `setters.yaml`.

Build from the upstream repository:

```bash
docker build -f build/quotascale-controller/Dockerfile \
  -t <registry>/quotascale-controller:<tag> .
docker push <registry>/quotascale-controller:<tag>
```

Then set:

```yaml
data:
  image-quotascale-controller: <registry>/quotascale-controller:<tag>
```

## Setters

| Setter | Default | Description |
| --- | --- | --- |
| `namespace` | `quotascale-controller` | Controller namespace |
| `image-quotascale-controller` | `ghcr.io/ssu-dcn/quotascale-controller:latest` | Controller image |
| `image-pull-policy` | `IfNotPresent` | Kubernetes image pull policy |
| `quota-check-interval-arg` | `--quota-check-interval=1m` | Periodic utilization check |
| `quota-update-interval-arg` | `--quota-update-interval=1m` | Per-namespace resize rate limit |
| `enable-node-scaling-arg` | `--enable-node-scaling=false` | Optional node-scaling controller |
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
`MachineDeployment`, plus repository credentials. It is intentionally disabled
in this base package. Enable it only after adding the upstream GitOps flags or
environment variables and a Kubernetes Secret through a site-specific package.
