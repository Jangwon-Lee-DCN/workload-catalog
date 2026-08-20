# QuotaScale Example KPT Package

This package deploys one `ResourceQuota` and one `QuotaAutoscaler` for testing
the QuotaScale Controller. Both resources target the `default` namespace.

## Resources

- `resourcequota.yaml`: `resource-quota-a`, initially limited to 4 CPU and 4Gi memory
- `quotaautoscaler.yaml`: `quota-test-a-autoscaler`, scaling between 4 and 15 CPU/Gi

The `QuotaAutoscaler` CRD and QuotaScale Controller must already be installed.

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
