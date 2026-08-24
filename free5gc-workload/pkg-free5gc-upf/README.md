# free5GC UPF kpt Package

This kpt package deploys the free5GC User Plane Function (UPF) v3.4.3 on an edge Kubernetes cluster using Multus CNI for multiple network interfaces.

## Package Contents

| File | Description |
|------|-------------|
| Kptfile | kpt package definition and function pipeline |
| setters.yaml | Configurable parameters (IPs, subnets, gateways) |
| package-context.yaml | kpt package context |
| namespace.yaml | Kubernetes Namespace: free5gc |
| upf.yaml | ConfigMap (UPF config), Deployment, Service |
| n3-nad.yaml | NetworkAttachmentDefinition for N3 (GTP-U, toward gNB) |
| n4-nad.yaml | NetworkAttachmentDefinition for N4 (PFCP, toward SMF) |
| n6-nad.yaml | NetworkAttachmentDefinition for N6 (DN, toward internet) |

## Prerequisites

1. **gtp5g kernel module** must be supported on the edge cluster nodes.
   The UPF uses the `gtp5g` forwarder for GTP-U packet processing.
   The init container runs `modprobe gtp5g` to load the module automatically,
   but the module must be present in the host kernel.

2. **Multus CNI** must be installed on the cluster.
   All three network interfaces (N3, N4, N6) are attached via Multus
   NetworkAttachmentDefinitions using macvlan over the `ens3` physical NIC.

3. **NetworkAttachmentDefinition CRD** from the k8s-sigs/network-attachment-definition project
   must be present on the cluster.

## NIC Configuration Note

All three Multus interfaces (N3, N4, N6) are configured to use `ens3` as the
master NIC (`upf-nad-master: ens3` in setters.yaml). This is the physical NIC
name on the edge cluster nodes. If your nodes use a different NIC name
(e.g., `eth0`, `ens4`, `enp3s0`), update the `upf-nad-master` setter before
rendering the package.

## Customizing IP Addresses

Edit `setters.yaml` to match your network addressing plan:

```yaml
data:
  upf-n3-ip: 192.168.12.201      # N3 interface IP (GTP-U toward gNB)
  upf-n3-subnet: "24"
  upf-n3-gateway: 192.168.12.1
  upf-n3-nad-master: ens8

  upf-n4-ip: 192.168.11.202      # N4 interface IP (PFCP toward SMF)
  upf-n4-subnet: "24"
  upf-n4-gateway: 192.168.11.1
  upf-n4-nad-master: ens7

  upf-n6-ip: 192.168.13.203      # N6 interface IP (toward data network)
  upf-n6-subnet: "24"
  upf-n6-gateway: 192.168.13.1
  upf-n6-nad-master: ens9

  ue-subnet: 10.1.0.0/16        # UE IP pool allocated by SMF
  dnn: internet                  # Data Network Name
  image-tag: v3.4.3             # UPF container image tag
```

`kpt fn render` propagates these values both to the NAD JSON strings and to the
embedded `upfcfg.yaml` data in the ConfigMap. Re-rendering after changing the
setters again is supported.

## Deploying the Package

### Render (apply setters) and deploy:

```bash
# Initialize the package (if fetched from a remote repo)
kpt pkg get <repo-url>/pkg-free5gc-upf free5gc-upf

# Render the package (applies setters and namespace mutation)
kpt fn render pkg-free5gc-upf/

# Preview what will be applied
kpt live init pkg-free5gc-upf/
kpt live apply pkg-free5gc-upf/ --dry-run

# Deploy to the cluster
kpt live apply pkg-free5gc-upf/
```

### Check status:

```bash
kpt live status pkg-free5gc-upf/
kubectl get pods -n free5gc -l app=upf
kubectl logs -n free5gc deployment/upf -c upf
```

## Network Architecture

```
gNB  ---[N3: 192.168.100.20/24]--- UPF ---[N6: 192.168.200.10/24]--- Internet
SMF  ---[N4: 192.168.101.20/24]--- UPF
```

- **N3**: GTP-U tunnel endpoint for user plane traffic from gNB
- **N4**: PFCP control interface connecting UPF to SMF
- **N6**: Data network interface for internet breakout

## Security Context

The UPF pod runs with `privileged: true` and the `NET_ADMIN` and `SYS_MODULE`
capabilities. This is required for:
- Loading the `gtp5g` kernel module via the init container
- Creating and managing GTP-U tunnel interfaces
- Manipulating routing tables and network namespaces
