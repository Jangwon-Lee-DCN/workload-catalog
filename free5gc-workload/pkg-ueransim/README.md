# pkg-ueransim

UERANSIM gNB and UE simulator package for free5GC, deployed on the edge cluster.

## Overview

This package deploys UERANSIM v3.2.6 (`towards5gs/ueransim:v3.2.6`) to simulate a 5G gNB (gNodeB) and UE (User Equipment) against a free5GC core network. The gNB uses two Multus NetworkAttachmentDefinitions to attach to the N2 (NGAP/control plane) and N3 (GTP-U/user plane) interfaces via macvlan on `ens3`. The UE deployment connects to the gNB through a Kubernetes ClusterIP Service.

## Prerequisites

- Multus CNI installed on the edge cluster
- free5GC control plane (AMF) reachable at the configured N2 IP
- free5GC UPF reachable at the configured N3 IP
- The UE subscriber must be registered in the free5GC WebUI **before** the UE pod starts

## PLMN Configuration

The PLMN (MCC/MNC) set in this package **must exactly match** the PLMN configured in the free5GC control plane (AMF, SMF, NRF). The defaults are:

- MCC: `001`
- MNC: `01`

If your free5GC deployment uses a different PLMN, update `plmn-mcc` and `plmn-mnc` in `setters.yaml` and re-run `kpt fn render`.

## Subscriber Registration

Before applying this package (or before the UE pod reaches Running state), register the subscriber in the free5GC WebUI:

1. Open the WebUI at `http://<free5gc-webui>:5000`
2. Go to Subscribers and click Add
3. Enter the IMSI matching `ue-imsi` in setters.yaml (default: `imsi-001010000000001`)
4. Set the K (key) matching `ue-key` (default: `8baf473f2f8fd09487cccbd7097c6862`)
5. Set the OPc matching `ue-opc` (default: `8e27b6af0e692e750f32667a3b14605d`)
6. Set the APN/DNN to match `ue-apn` (default: `internet`)
7. Set SST=1, SD=ffffff (or match your slice setters)
8. Save the subscriber

If the UE pod starts before the subscriber is registered, it will fail authentication. Restart the UE pod after registration.

## Verifying the UE Got an IP Address

After the UE pod is Running, check for the `uesimtun0` tunnel interface:

```bash
# List UE pods
kubectl -n free5gc get pods -l app=ue

# Check tunnel interface inside the UE pod
kubectl -n free5gc exec -it deployment/ue -- ip addr show uesimtun0

# Alternatively check all interfaces
kubectl -n free5gc exec -it deployment/ue -- ip addr

# Test data plane connectivity through the tunnel
kubectl -n free5gc exec -it deployment/ue -- ping -I uesimtun0 8.8.8.8
```

A successful attach will show `uesimtun0` with an IP address assigned by the UPF (typically from the UE IP pool configured in free5GC SMF).

## Checking gNB Status

```bash
# Check gNB pod logs for NGAP connection to AMF
kubectl -n free5gc logs -l app=gnb --tail=50

# Verify Multus interfaces are attached
kubectl -n free5gc exec -it deployment/gnb -- ip addr
```

## kpt Setters Reference

Edit `setters.yaml` and run `kpt fn render` to apply changes:

| Setter | Default | Description |
|---|---|---|
| `namespace` | `free5gc` | Kubernetes namespace for all resources |
| `gnb-n2-ip` | `192.168.10.204` | gNB N2 (NGAP) interface IP |
| `gnb-n2-subnet` | `24` | N2 interface subnet prefix length |
| `gnb-n2-gateway` | `192.168.10.1` | N2 interface default gateway |
| `gnb-n2-nad-master` | `ens6` | Host NIC for the gNB N2 ipvlan |
| `gnb-n3-ip` | `192.168.12.205` | gNB N3 (GTP-U) interface IP |
| `gnb-n3-subnet` | `24` | N3 interface subnet prefix length |
| `gnb-n3-gateway` | `192.168.12.1` | N3 interface default gateway |
| `gnb-n3-nad-master` | `ens8` | Host NIC for the gNB N3 ipvlan |
| `amf-n2-ip` | `192.168.10.200` | AMF N2 IP (regional cluster) |
| `upf-n3-ip` | `192.168.12.201` | UPF N3 IP (edge cluster) |
| `aws-region` | `ap-southeast-1` | AWS region segment used in worker node names |
| `edge-worker-node-ip` | `ip-192-168-1-11` | EC2 private-DNS node prefix for gNB and UE scheduling |
| `plmn-mcc` | `001` | PLMN Mobile Country Code |
| `plmn-mnc` | `01` | PLMN Mobile Network Code |
| `tac` | `1` | Tracking Area Code |
| `sst` | `1` | Slice/Service Type |
| `sd` | `ffffff` | Slice Differentiator |
| `dnn` | `internet` | Data Network Name |
| `ue-imsi` | `imsi-001010000000001` | UE IMSI (must match WebUI subscriber) |
| `ue-key` | `8baf473f2f8fd09487cccbd7097c6862` | UE authentication key K |
| `ue-opc` | `8e27b6af0e692e750f32667a3b14605d` | UE OPc value |
| `ue-apn` | `internet` | UE default APN/DNN |
| `gnb-id` | `0x000001` | gNB identifier |
| `image-tag` | `v3.2.6` | UERANSIM Docker image tag |

## Applying the Package

```bash
# Render setters
kpt fn render pkg-ueransim/

# Apply to cluster
kpt live init pkg-ueransim/
kpt live apply pkg-ueransim/
```
