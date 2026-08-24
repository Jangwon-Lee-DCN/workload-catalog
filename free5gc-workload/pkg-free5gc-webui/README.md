# free5GC WebUI kpt Package

This package deploys the free5GC WebUI on a regional cluster alongside the free5GC Control Plane (CP).

## Overview

- **Namespace**: `free5gc`
- **Image**: `free5gc/webui:v3.4.3`
- **MongoDB**: connects to `mongodb://mongodb:27017` (same namespace)
- **Exposed**: NodePort `30500` (HTTPS)

## Access

Once deployed, access the WebUI at:

```
https://NODE_IP:30500
```

Replace `NODE_IP` with the IP address of any node in your regional cluster.

### Default Login Credentials

| Field    | Value    |
|----------|----------|
| Username | `admin`  |
| Password | `free5gc` |

> **Security note**: Change the default password immediately after first login in production environments.

## Automatic Subscriber Registration

The package creates the following subscriber automatically. Slice, DNN, QoS, and charging
settings use the defaults presented by free5GC WebUI v3.4.3. The bootstrap Job waits for
MongoDB and the WebUI `admin` tenant, then inserts any missing subscriber documents.
Existing documents are never overwritten, so a live authentication SQN is not reset by a
package re-apply.

| Field | Default |
|-------|---------|
| SUPI / IMSI | `imsi-001010000000001` |
| PLMN ID | `00101` |
| MCC | `001` |
| MNC | `01` |
| Authentication method | `5G_AKA` |
| Permanent key (K) | `8baf473f2f8fd09487cccbd7097c6862` |
| Operator code type | `OPC` |
| Operator code value (OPc) | `8e27b6af0e692e750f32667a3b14605d` |
| AMF | `8000` |
| SQN | `000000000000` |

`subscriber-plmn-id` must be the concatenation of `subscriber-mcc` and `subscriber-mnc`.
The bootstrap Job fails without modifying subscriber data when these values disagree.

## How to Add Another Subscriber

Subscribers must be added to the WebUI **before** a UE (User Equipment) attempts to connect. Attempting to connect without a registered subscriber will result in authentication failure.

### Steps

1. Log in to the WebUI at `https://NODE_IP:30500`.
2. Navigate to **Subscribers** in the left sidebar.
3. Click **New Subscriber**.
4. Fill in the required fields:

   | Field | Description | Example |
   |-------|-------------|---------|
   | **IMSI** | International Mobile Subscriber Identity (15 digits) | `208930000000001` |
   | **K** | Authentication key (32 hex characters) | `8baf473f2f8fd09487cccbd7097c6862` |
   | **OPc** | Operator code (computed from OP and K; 32 hex characters) | `8e27b6af0e692e750f32667a3b14605d` |
   | **AMF** | Authentication Management Field | `8000` |
   | **SQN** | Sequence number | `000000000000` |

5. Configure the **S-NSSAI** (network slice) and **DNN** (Data Network Name) as required by your deployment. Default slice is SST=1 with DNN `internet`.
6. Click **Submit** to register the subscriber.

### Important Notes

- The subscriber record must exist in MongoDB **before** the UE powers on or attaches.
- IMSI format: MCC (3 digits) + MNC (2-3 digits) + MSIN. Example MCC=208, MNC=93.
- K and OPc values must match the SIM card or UE simulator configuration exactly.
- If using Open5GS or UERANSIM as the UE simulator, ensure K and OPc in the simulator config match the values entered here.

## Package Configuration (Setters)

Customize the package by editing `setters.yaml` before running `kpt fn render`:

| Setter | Default | Description |
|--------|---------|-------------|
| `namespace` | `free5gc` | Kubernetes namespace |
| `mongodb-uri` | `mongodb://mongodb:27017` | MongoDB connection URI |
| `image-webui` | `free5gc/webui:v3.4.3` | WebUI container image |
| `image-mongodb` | `mongo:4.4` | Subscriber bootstrap container image |
| `service-type` | `NodePort` | Kubernetes Service type |
| `node-port` | `30500` | NodePort number for external access |
| `subscriber-supi` | `imsi-001010000000001` | SUPI including the `imsi-` prefix |
| `subscriber-plmn-id` | `00101` | Serving PLMN ID |
| `subscriber-mcc` | `001` | MCC; must match the PLMN ID |
| `subscriber-mnc` | `01` | MNC; must match the PLMN ID |
| `subscriber-auth-method` | `5G_AKA` | Authentication method |
| `subscriber-permanent-key` | `8baf...6862` | Permanent authentication key (K) |
| `subscriber-opc` | `8e27...605d` | OPc value; operator code type is OPC |
| `subscriber-amf` | `8000` | Authentication Management Field |
| `subscriber-sqn` | `000000000000` | SQN used only when the subscriber does not exist |

## Deployment

```bash
# Render the package (apply setters and set-namespace)
kpt fn render pkg-free5gc-webui/

# Apply to the cluster
kpt live init pkg-free5gc-webui/
kpt live apply pkg-free5gc-webui/
```

## Dependencies

- MongoDB must be running in the `free5gc` namespace and accessible at the configured URI before the WebUI starts.
- The free5GC Control Plane (AMF, SMF, UPF, etc.) should be deployed in the same namespace.
