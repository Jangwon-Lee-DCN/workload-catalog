# Nephio·Porch 기반 Core·Edge 서비스 배포

## 1. 배포 방법

관리 클러스터의 Nephio WebUI에서 다음 순서로 진행한다.

1. 카탈로그 `catalog-ims-demo`에서 표에 적힌 패키지를 선택한다.
2. 표에 적힌 대상 Repository로 복제한다.
3. Draft의 `setters.yaml`에서 **수정 필요** 항목만 바꾼다. 나머지는 기본값을 사용한다.
4. 렌더링 → 제안 → 승인·게시한다.
5. 해당 단계의 완료 조건을 확인한 뒤 다음 패키지를 배포한다.

이미 배포한 패키지는 다시 복제하지 않고, 환경값을 변경할 때만 새 Draft로 수정·게시한다. Core·Edge 서비스는 Porch가 Git 저장소에 기록하고 각 클러스터의 ArgoCD가 적용한다.

## 2. 사용 환경과 기본값

| 항목 | 기본값 | 수정 여부 |
|---|---|---|
| 관리 namespace | `default` | 현재 관리 환경이 같으면 유지. |
| 관리 Repository | `mgmt` | 유지. |
| Core 클러스터·Repository | `core` | 유지. 검증 환경도 같은 이름 사용. |
| Edge 클러스터·Repository | `edge` | 유지. 검증 환경도 같은 이름 사용. |
| GPU 클러스터 | `demo-gpu-a` | GPU 패키지와 같은 이름 유지. |
| Core·Edge worker IP | `172.31.81.10`, `172.31.81.11` | 제공한 ENI 주소 계획을 사용하면 유지. |
| N2·N3·N4·N6 주소, NIC 이름 | 제공한 172.31 대역·`ens6`~`ens9` | 같은 주소 계획이면 유지. |
| IMS 도메인·가입자·이미지 | 패키지 기본값 | 유지. |
| DB·IMS 비밀번호, 생성 어댑터 토큰 | `password` | 제공한 데모 설정으로 유지. |
| 음성 생성 경로 | `gpu_local` | 유지. ElevenLabs 계정 입력 불필요. |

**기존 주소 계획을 그대로 쓰면 Core·Edge 서비스의 설정 대부분은 바꾸지 않는다.** 새로 생성한 AWS 리소스 ID, 관리 Gitea 주소, 공개 웹 접속값만 해당 단계에서 맞춘다.

## 3. 단계별 패키지 배포

아래 패키지 경로는 이 저장소의 루트를 기준으로 한다. 실제 파일명은 `setters.yaml`이다.

| 순서 | 패키지 | 대상 Repository | `setters.yaml` 수정 필요 항목 | 그대로 사용할 항목 | 배포 여부·다음 단계 조건 |
|---|---|---|---|---|---|
| 선행 | `infra/capa-free5gc/workload-repository` | `mgmt` | 다른 카탈로그 주소·브랜치를 사용할 때만 `catalog-url`, `catalog-branch` 변경. | `catalog-name: catalog-ims-demo`, `namespace: default`. | 카탈로그가 없을 때만 배포. 이미 있으면 생략. |
| A1 | `infra/capa-free5gc/eni-controller` | `mgmt` | 기본 환경에서는 수정 없음. | 공개 controller 이미지와 설정. | Controller·CRD가 이미 있으면 생략. 없으면 배포. |
| A2 | `infra/capa-free5gc/eni-pool` | `mgmt` | `vpc-id`, `security-group-id`, `eni-retention-security-group-id`, 고정 ENI ID 8개. | 계획한 primary·secondary IP, 연결 순서, worker 이름. | 새 VPC·ENI를 쓸 때 배포·갱신. 같은 pool이 이미 준비됐다면 생략. |
| A3 | `infra/capa-free5gc/aws-clusters` | `mgmt` | A2와 같은 VPC·SG·ENI ID. `public-subnet-id`, `private-subnet-id`, `management-git-host`, `management-git-port`. 키 페어가 다르면 `ssh-key-name`. | `core-cluster-name: core`, `edge-cluster-name: edge`, 서울 AZ·AMI·VM 사양·노드 IP. | Core·Edge 클러스터를 만들 때 배포. 두 클러스터의 Node Ready와 Repository `core`·`edge` 준비 확인. |
| A4 | `free5gc-ims/core` | `core` | **수정 없음.** 주소 계획을 변경한 경우에만 해당 IP·node-name 변경. | Core·IMS·가입자·비밀번호·이미지·`inspection-enabled: 'false'`. | A3 이후 배포. Core Application `Synced/Healthy`, 가입자 Job `Complete` 확인. |
| A5 | `infra/capa-free5gc/cluster-bindings` | `mgmt` | **수정 없음.** | `core-cluster-name: core`, `edge-cluster-name: edge`. | A4 이후 배포. Core 관측 정보를 Edge로 자동 전달. 연결 Deployment Ready 확인. |
| A6 | `free5gc-ims/edge` | `edge` | `phone-hostname`, `public-subnet-id`, `public-eip-allocation-id`. 접근 대역을 바꿀 때만 `public-source-cidrs`. | UE·UPF·gNB·IMS 주소, `generation-provider: gpu_local`, `inspection-enabled: 'true'`, 토큰·이미지. | A5 이후 배포. GPU 연결 전에는 관련 Pod가 대기할 수 있음. B4 완료 후 자동 기동. |

A3에서 CNI·Multus·ArgoCD·클러스터별 저장소가 함께 준비된다. 설치자가 이를 별도로 설치하지 않는다. Core·Edge의 Secret도 서비스 패키지에 포함된다.

### A6에서 바꿀 값

`free5gc-ims/edge/setters.yaml`의 `data`에서 아래 항목만 실제 리소스로 바꾼다. 예시의 AWS ID는 설치 환경의 ID로 대체한다.

```yaml
  phone-hostname: voice.3.35.1.158.sslip.io
  public-subnet-id: subnet-0123456789abcdef0
  public-eip-allocation-id: eipalloc-0123456789abcdef0
```

| 항목 | 넣을 값 |
|---|---|
| `phone-hostname` | `voice.<웹 접속용 EIP 주소>.sslip.io`. |
| `public-subnet-id` | Core·Edge VPC에 준비한 공개 subnet ID. |
| `public-eip-allocation-id` | 같은 웹 접속용 EIP의 Allocation ID. |
| `public-source-cidrs` | 기존 학교망·접속 대역을 유지하면 수정 없음. 추가할 대역이 있을 때만 변경. |

HTTPS 인증서와 NLB는 Edge 패키지에서 생성한다. 인증서 파일을 따로 만들거나 입력하지 않는다.

## 4. GPU 경로와 합류

[GPU 클러스터·서비스 배포](../gpu/README.md)는 A1~A6와 병렬로 진행한다.

| 순서 | 패키지·추가 작업 | 대상 | 수정 필요 항목 | 배포 시점 |
|---|---|---|---|---|
| B1 | `infra/capa-free5gc/gpu-cluster` | `mgmt` | VPC·공개 subnet ID. 다른 키 페어를 쓰면 SSH 키 이름. | Core·Edge 구축과 병렬로 배포. |
| B2 | `gpu-services/inject-aisrc.sh` | 관리 호스트에서 실행. | archive·SSH 키의 파일 경로. | GPU Node Ready 이후 1회 실행. |
| B3 | `infra/capa-free5gc/gpu-services` | `mgmt` | 기본 환경이면 수정 없음. | B2 전송 완료 후 배포. 하위 GPU 패키지는 자동 전달. |
| B4 | `infra/capa-free5gc/gpu-bindings` | `mgmt` | 기본 환경이면 수정 없음. | B3 게시 후 배포. GPU API·Edge API 준비를 자동 대기. |

A6는 B4 완료를 기다리지 않고 게시한다. B4가 GPU 공개 API 주소·토큰을 Edge에 전달하면 대기 중인 전화·검사 서비스가 기동한다. GPU 주소·토큰을 Core·Edge의 `setters.yaml`에 직접 입력하지 않는다.

## 5. 완료 확인

| 위치 | 확인할 상태 |
|---|---|
| 관리 클러스터 | Core·Edge·GPU Cluster 준비, 연결 Deployment Ready. |
| Core | ArgoCD Application `core`: `Synced/Healthy`, 가입자 Job `Complete`. |
| Edge | ArgoCD Application `edge`: `Synced/Healthy`, 공개 Certificate Ready. |
| 웹 | `https://<phone-hostname>/ims/1001/`, `/ims/1002/`: 양방향 통화·음성 생성·판별. |
| 관측 | `https://<phone-hostname>/ims/observe/`: 실제 판별 Pod `0→1→2→0`. |

명령으로 상태를 확인할 때는 준비된 kubeconfig를 사용한다.

```bash
# 관리 클러스터
kubectl -n default get clusters
kubectl -n default get repositories.config.porch.kpt.dev core edge
kubectl -n default get deployment ims-cluster-bindings ims-gpu-bindings

# Core·Edge
kubectl --kubeconfig core.kubeconfig -n argocd get application core
kubectl --kubeconfig core.kubeconfig -n ims-lab get jobs
kubectl --kubeconfig edge.kubeconfig -n argocd get application edge
kubectl --kubeconfig edge.kubeconfig -n ims-lab get certificate,ingress
```

전체 배포 순서·병렬 관계는 [배포 다이어그램](../../infra/capa-free5gc/docs/INSTALL.md#1-패키지-배포-순서), 개별 설정 키는 [설정 표](PARAMETERS.md)에 있다.
