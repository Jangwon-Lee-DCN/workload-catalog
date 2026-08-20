# QuotaScale Example KPT Package

This package deploys one `ResourceQuota` and one `QuotaAutoscaler` for testing
the QuotaScale Controller. Both resources target the `default` namespace.

## Resources

- `resourcequota.yaml`: `resource-quota`, initially limited to 6 CPU and 6Gi memory
- `quotaautoscaler.yaml`: `quota-autoscaler`, scaling between 6 and 25 CPU/Gi

The `QuotaAutoscaler` CRD and QuotaScale Controller must already be installed.

## Argo CD ownership

Both resources have the `argocd.argoproj.io/hook: Skip` annotation. Argo CD
therefore does not create, update, replace, or prune them during synchronization,
so values changed by the QuotaScale Controller are not reset to the Git values.

The resources must be created separately (for example with `kpt live apply` or
`kubectl apply`) before relying on the Argo CD deployment. Remove the `Skip`
annotation temporarily if Argo CD should perform the initial creation.

## Setter

| Setter | Default | Description |
| --- | --- | --- |
| `namespace` | `default` | Namespace for both example resources |

## Render and apply

```bash
kpt fn render infra/quotascale-example
kpt live init infra/quotascale-example
kpt live apply infra/quotascale-example
```
