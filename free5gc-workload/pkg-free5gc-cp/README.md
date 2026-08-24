# free5GC Control Plane kpt Package

This kpt package deploys the free5GC v3.4.3 Control Plane into a regional Kubernetes cluster.

## Components

| Component | Role | Interface |
|-----------|------|-----------|
| MongoDB   | Subscriber database backend | ClusterIP :27017 |
| NRF       | Network Repository Function | SBI HTTPS :8000 |
| UDR       | Unified Data Repository | SBI HTTPS :8000 |
| UDM       | Unified Data Management | SBI HTTPS :8000 |
| AUSF      | Authentication Server Function | SBI HTTPS :8000 |
| AMF       | Access and Mobility Management | SBI :8000 + NGAP SCTP :38412 (N2 via Multus macvlan) |
| SMF       | Session Management Function | SBI :8000 + PFCP UDP :8805 (N4 via pod IP) |

## Prerequisites

1. Kubernetes cluster with:
   - Multus CNI installed and configured
   - A storage class available for MongoDB PVC (default: `standard`)
   - SCTP kernel module loaded on nodes running AMF (`modprobe sctp`)

2. kpt CLI >= v1.0 installed (`https://kpt.dev/installation/`)

3. Network topology:
   - **N2 subnet** (e.g., 192.168.100.0/24) reachable from gNBs, bridged to NIC `ens3` on cluster nodes
   - **N4 route** from edge UPF (192.168.101.20) back to the AMF pod network, so PFCP responses reach SMF

## Configuring setters.yaml

Edit `setters.yaml` to match your environment before rendering. The key parameters are:

### Network Identity

| Setter | Default | Description |
|--------|---------|-------------|
| `namespace` | `free5gc` | Kubernetes namespace for all resources |
| `plmn-mcc` | `001` | Mobile Country Code |
| `plmn-mnc` | `01` | Mobile Network Code |
| `tac` | `1` | Tracking Area Code |

### AMF N2 Interface (Multus ipvlan)

| Setter | Default | Description |
|--------|---------|-------------|
| `amf-n2-ip` | `192.168.10.200` | Static IP assigned to the AMF N2 interface |
| `amf-n2-subnet` | `24` | Prefix length for the N2 subnet |
| `amf-n2-gateway` | `192.168.10.1` | Default gateway for the N2 interface |
| `amf-n2-nad-master` | `ens6` | Host NIC to attach the ipvlan to |
| `amf-port` | `38412` | SCTP port for NGAP |

### UPF / N4 (PFCP)

| Setter | Default | Description |
|--------|---------|-------------|
| `smf-n4-ip` | `192.168.11.176` | N4 IP address assigned to SMF |
| `smf-n4-subnet` | `24` | Prefix length for the SMF N4 subnet |
| `smf-n4-gateway` | `192.168.11.1` | Gateway for the SMF N4 interface |
| `smf-n4-nad-master` | `ens7` | Host NIC for the SMF N4 ipvlan |
| `upf-n4-ip` | `192.168.11.202` | N4 IP address of the UPF (edge cluster) |
| `upf-n3-ip` | `192.168.12.201` | N3 IP address of the UPF (edge cluster) |

### Slice & DNN

| Setter | Default | Description |
|--------|---------|-------------|
| `sst` | `1` | Slice/Service Type |
| `sd` | `ffffff` | Slice Differentiator |
| `dnn` | `internet` | Data Network Name |
| `ue-subnet` | `10.1.0.0/16` | UE IP address pool CIDR |
| `ue-dns` | `8.8.8.8` | DNS server pushed to UEs |

### Infrastructure

| Setter | Default | Description |
|--------|---------|-------------|
| `image-tag` | `v3.4.3` | Docker image tag for all free5GC NFs |
| `storage-class` | `standard` | StorageClass name for MongoDB PVC |
| `mongodb-uri` | `mongodb://mongodb:27017` | MongoDB connection URI used by NRF/UDR |
| `aws-region` | `ap-southeast-1` | AWS region segment used in worker node names |
| `core-worker-node-ip` | `192.168.1.10` | EC2 private IP for AMF and SMF scheduling; rendered to AWS private DNS form |

The render pipeline applies ordinary YAML setters first, then runs the package's
Starlark mutator so the same values are also updated inside embedded free5GC
configuration files. NAD JSON strings are generated from the IP, prefix, gateway,
and master-interface setters.
| `nrf-service-name` | `nrf-service` | Kubernetes service name for NRF |

## Deployment

### 1. Fetch / initialize the package

```bash
# If pulling from a remote blueprint repository:
kpt pkg get oci://YOUR_OCI_REPO/free5gc-cp@v1.0.0 ./free5gc-cp

# Or work directly in this directory after cloning:
cd pkg-free5gc-cp
```

### 2. Edit setters

```bash
# Open setters.yaml and adjust values for your target cluster:
vi setters.yaml
```

### 3. Render the package (applies all kpt functions)

```bash
kpt fn render .
```

This runs `apply-setters` (substitutes all `# kpt-set:` tokens) followed by
`set-namespace` (forces all resources into the configured namespace).

### 4. Review the rendered output

```bash
kpt pkg diff .
```

### 5. Deploy to the cluster

```bash
# Create namespace first if it does not exist:
kubectl apply -f namespace.yaml

# Apply the full package:
kpt live init .          # first time only — creates the ResourceGroup inventory object
kpt live apply .
```

### 6. Verify

```bash
kubectl -n free5gc get pods
kubectl -n free5gc logs deploy/amf -f
kubectl -n free5gc logs deploy/smf -f
```

## Network Architecture Notes

### AMF N2 (NGAP / SCTP)

The AMF uses a Multus `NetworkAttachmentDefinition` (`free5gc-amf-n2`) to attach a macvlan
interface directly to `ens3` on the worker node. This gives AMF a stable IP address on the
RAN-facing N2 subnet (default `192.168.100.10/24`) that gNBs can reach independently of
Kubernetes service networking.

The `amf-ngap` Service exposes SCTP port 38412 as a NodePort (30412) as a secondary access
path when direct macvlan routing is not configured.

### SMF N4 (PFCP / UDP)

SMF does **not** use Multus. It sends PFCP messages from its pod IP. For this to work:

- The Kubernetes node network must be routable from the edge UPF's N4 interface.
- The UPF must have a return route pointing to the pod CIDR via the N4 gateway.
- SMF's `pfcp.externalAddr` is populated from the `POD_IP` downward API environment variable.

### Startup Order

The `initContainers` in each NF enforce the following dependency order:

```
MongoDB -> NRF -> UDR -> UDM -> AUSF -> AMF -> SMF
```

## TLS Certificates

The default config uses self-signed certificates bundled inside the free5GC container image
at `config/TLS/`. For production use, replace these by mounting a Secret with proper
certificates at the same paths.

## Upgrading

Change `image-tag` in `setters.yaml`, run `kpt fn render .`, then `kpt live apply .`.
MongoDB data is persisted in the PVC and survives NF pod restarts.
