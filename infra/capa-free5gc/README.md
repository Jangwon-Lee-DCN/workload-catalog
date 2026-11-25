# free5GC Core·Edge CAPA KPT

관리 클러스터의 기존 `core-cluster`, `edge-cluster` 원형을 기반으로 새 환경용 패키지를 구성했다. Core·Edge CNF를 적용하기 전에 **관리 클러스터**에서 적용한다. GPU 클러스터와는 별도다. 수동 실행은 [설치 절차](docs/INSTALL.md)를 따른다.

| 항목 | 기본값 |
|---|---|
| 관리 클러스터 선행 구성 | CAPI 1.14.3, CAPA 2.13.1, kubeadm bootstrap/control-plane provider, cert-manager 1.18.2. |
| Core·Edge | 각각 control-plane 1개 + worker 1개. Kubernetes 1.32.0. |
| CPU 노드 AMI | 원형의 `ami-045715a39cc1c8a78`. Ubuntu 22.04 CAPA 기반. GPU용 AMI와 다름. |
| EC2 | control-plane `t3.large`, worker `c5.4xlarge`, root volume 100 GiB. |
| Region·AZ | `ap-northeast-2` · `ap-northeast-2a`. ENI·subnet과 같은 AZ로 설정. |
| Worker 고정 주소 | Core `172.31.81.10`, Edge `172.31.81.11`. |
| 기본 인터페이스 | `ens5`: 고정 primary ENI에서 DHCP로 같은 주소 수신. |
| 데이터 인터페이스 | Core `ens6~7`, Edge `ens6~9`. IP는 CNF의 Multus 인터페이스가 사용. |
| 초기 구성 | ENI controller·Pool, CAPI 리소스, 원형 CCM·CSI CRS와 Nephio mgmt-staging의 CNI·ArgoCD 패키지. |
| 인증 | CAPA의 기존 AWS 인증과 IAM instance profile 사용. 소스에 AWS 키 없음. |

## 1. 주소와 ENI

### 배포 시작

ENI controller·ENIPool이 준비돼 있으면 `aws-clusters` 상위 KPT부터 적용한다. [설치 절차](docs/INSTALL.md)의 값으로 `aws-clusters/setters.yaml`을 수정하고 KPT로 렌더링한다.

```bash
kpt fn render aws-clusters
kpt live init aws-clusters --namespace default --name free5gc-aws-clusters
kpt live apply aws-clusters --context management --reconcile-timeout=30m
```

Core·Edge의 CNI·ArgoCD·루트 Application은 `PackageVariant → mgmt-staging → Nephio bootstrap`으로 설치한다. 클러스터별 Repository 패키지는 `mgmt`에 게시된다. Python 설치 도구는 필요하지 않다.

### ENI별 IP 주소와 역할

| ENI | Primary IP | Secondary IP·사용 기능 | EC2 | Interface | Device index | 역할 |
|---|---|---|---|---|---|---|
| `core_primary_eni` | `172.31.81.10` | 없음 | Core worker | `ens5` | 0 | 기본·관리망 |
| `edge_primary_eni` | `172.31.81.11` | 없음 | Edge worker | `ens5` | 0 | 기본·관리망 |
| `core_n2_eni` | `172.31.90.10` | `172.31.90.200` (AMF) | Core worker | `ens6` | 1 | N2: AMF ↔ gNB 제어 신호 |
| `core_n4_eni` | `172.31.91.176` | 없음 | Core worker | `ens7` | 2 | N4: SMF ↔ UPF 제어 신호. SMF가 Primary IP 사용 |
| `edge_n2_eni` | `172.31.90.20` | `172.31.90.204` (gNB) | Edge worker | `ens6` | 1 | N2: gNB ↔ AMF 제어 신호 |
| `edge_n4_eni` | `172.31.91.20` | `172.31.91.202` (UPF) | Edge worker | `ens7` | 2 | N4: UPF ↔ SMF 제어 신호 |
| `edge_n3_eni` | `172.31.92.20` | `172.31.92.201` (UPF)<br>`172.31.92.205` (gNB) | Edge worker | `ens8` | 3 | N3: gNB ↔ UPF 사용자 트래픽 |
| `edge_n6_eni` | `172.31.93.20` | `172.31.93.203` (UPF)<br>`172.31.93.210` (P-CSCF)<br>`172.31.93.211` (RTPengine)<br>`172.31.93.213` (MEC 음성 검사) | Edge worker | `ens9` | 4 | N6: 사용자 데이터망·IMS·MEC 음성 처리 연결 |

고정 ENI는 Core worker 3개와 Edge worker 5개로 총 8개다. Control-plane·NAT VM의 기본 ENI는 이 표에 포함하지 않는다.

| subnet | CIDR |
|---|---|
| VPC | 172.31.0.0/16. |
| Public | 172.31.80.0/24. |
| Private | 172.31.81.0/24. |
| N2 / N4 / N3 / N6 | 172.31.90.0/24 / 172.31.91.0/24 / 172.31.92.0/24 / 172.31.93.0/24. |

ENI와 모든 주소를 AWS에 미리 할당한다. ENI controller는 주소를 새로 생성하지 않고 **ENI 묶음을 예약**한다. CAPA는 primary ENI로 EC2를 생성하고, controller가 나머지를 순서대로 연결한다. ENI에 지정된 primary·secondary 주소가 함께 유지된다.

대상 VM은 Worker `AWSMachineTemplate.spec.template.metadata.annotations`에 지정한다.

```yaml
spec:
  template:
    metadata:
      annotations:
        eni.dcn.ssu.ac.kr/allocate-from-pool: "true"
        eni.dcn.ssu.ac.kr/interface-key: edge_primary_eni
        eni.dcn.ssu.ac.kr/additional-interface-keys: edge_n2_eni,edge_n4_eni,edge_n3_eni,edge_n6_eni
        eni.dcn.ssu.ac.kr/attach-additional-interfaces: "true"
```

`ENIPool.spec.interfaces[].key`가 실제 ENI ID·primary IP를 가리킨다. 생성되는 AWSMachine에 annotation이 전달되고, 예약 ENI마다 생성한 ENIClaim의 `spec.machineRef`가 그 AWSMachine의 namespace·이름을 가리킨다. CAPA가 기록한 `AWSMachine.spec.instanceID`로 연결 대상 EC2를 찾는다. 추가 목록의 첫 항목부터 device index 1·2·3·4를 사용한다. Core는 같은 구조에서 primary key를 `core_primary_eni`, 추가 목록을 `core_n2_eni,core_n4_eni`로 지정한다.

Core는 `primary → N2 → N4`, Edge는 `primary → N2 → N4 → N3 → N6` 순서다. 누락·사용 중인 ENI가 있으면 생성 요청을 거부하며 동적 IP로 대체하지 않는다. 고정 ENI의 재사용을 위해 worker 교체는 기존 worker 삭제 후 새 worker 생성 순서로 진행한다.

SMF는 N4 ENI의 primary 주소 `.176`을 그대로 쓴다. bootstrap이 데이터 NIC의 호스트 DHCP를 끄므로, 호스트와 SMF가 같은 주소를 동시에 가지지 않는다. IMDS로 ENI ID·device index·ens 이름을 확인한 뒤 kubeadm을 진행한다.

## 2. 전체 배포 순서

[설치 절차의 패키지 배포 다이어그램](docs/INSTALL.md#1-패키지-배포-순서)에 Core·Edge·GPU 전체 순서와 AISRC 파일 주입 위치를 정리했다. Edge 패키지는 `cluster-bindings` 다음에 게시하고, GPU 경로는 독립적으로 진행한다. 두 경로는 전체 서비스의 최종 기동 확인에서 합류한다. 각 단계의 적용 위치와 완료 조건도 같은 절의 표에서 확인한다.

## Core·Edge 서비스 연결

Core 서비스를 게시한 뒤 관리 클러스터에서 `cluster-bindings` KPT를 배포한다. CAPA의 Core·Edge kubeconfig Secret을 사용해 읽기 전용 관측 자격 정보와 Core API 주소를 Edge에 자동 전달한다. 실행 순서는 [서비스 설치 절차](../../free5gc-ims/docs/INSTALL.md)의 4절을 따른다.

단일 GPU 클러스터는 `gpu-cluster`, GPU와 Edge의 주소·토큰 연결은 `gpu-bindings` 패키지를 사용한다. [GPU·FaaS 설치 순서](../../free5gc-ims/gpu/README.md)를 따른다. AISRC 앱·모델·인증 파일만 별도로 전달하여 주입한다.
