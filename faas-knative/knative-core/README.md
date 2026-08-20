# knative-core

## Description

Knative Serving 1.15 core and Kourier ingress for the edge cluster. Queue-proxy
resource defaults are enabled so injected sidecars satisfy namespaces that
enforce CPU and memory requests and limits through `ResourceQuota`.

## Setters

| Setter | Default | Description |
| --- | --- | --- |
| `queueproxy-resource-defaults` | `enabled` | Apply default requests and limits to queue-proxy containers |
| `edge-node-ip` | `192.168.1.11` | Edge worker IP exposed by the Kourier NodePort service |

## Usage

### Fetch the package
`kpt pkg get REPO_URI[.git]/PKG_PATH[@VERSION] knative-core`
Details: https://kpt.dev/reference/cli/pkg/get/

### View package content
`kpt pkg tree knative-core`
Details: https://kpt.dev/reference/cli/pkg/tree/

### Apply the package
```
kpt live init knative-core
kpt live apply knative-core --reconcile-timeout=2m --output=table
```
Details: https://kpt.dev/reference/cli/live/
