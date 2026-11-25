# 단일 GPU 클러스터·전화 데모 모델 배포

## 1. 기본 구성

| 항목 | 기본값 | 수정 여부 |
|---|---|---|
| 배포 위치 | 관리 클러스터, Repository `mgmt`, namespace `default`. | 유지. |
| GPU 클러스터 이름 | `demo-gpu-a`. | B1·B2·B3·B4에서 동일하게 유지. |
| 리전·노드 | 서울 `ap-northeast-2a`, `g6.8xlarge`, L4 24 GB 1장, 32 vCPU, RAM 128 GiB, gp3 400 GiB. | 같은 환경이면 유지. |
| CAPA 이미지 | 공개 Ubuntu 24.04 AMI `ami-0f0bd37b402de10d7`. | 서울에서는 유지. 비공개 AMI 불필요. |
| 노드 소프트웨어 | Kubernetes·CRI-O 1.33.13, NVIDIA 580.178.04, Toolkit 1.20.1. | 패키지에서 자동 설치. |
| GPU 공유·FaaS | 표준 device plugin 공유 슬롯 6개, Knative·Kourier 1.21.0. | 자동 구성. |
| 모델 | Fake Voice Detection 모델 (Source: AISRC), Qwen3-TTS-12Hz-1.7B-Base. | 자동 배포. 각각 최대 2 Pod·1 Pod. |
| 생성 내용 확인 | CPU STT: faster-whisper large-v3-turbo. | 자동 배포. |

Core·Edge 구축과 병렬로 진행한다. [전체 순서](../../infra/capa-free5gc/docs/INSTALL.md#1-패키지-배포-순서)의 B1→B2→B3→B4 순서를 따른다.

## 2. 단계별 수정·배포

Nephio WebUI에서 카탈로그 `catalog-ims-demo`의 패키지를 `mgmt`로 복제하고, 아래 항목만 수정한 뒤 **렌더링 → 제안 → 승인·게시**한다. 이미 게시한 패키지는 변경할 때만 새 Draft를 만든다.

| 순서 | 패키지·작업 | 수정할 파일·항목 | 그대로 사용할 항목 | 배포 시점·완료 조건 |
|---|---|---|---|---|
| B1 | `infra/capa-free5gc/gpu-cluster` | `setters.yaml`: `vpc-id`, `public-subnet-id`. 다른 키 페어를 쓰면 `ssh-key-name`. | GPU 이름·namespace·서울 AZ·AMI·VM 사양·IAM profile·버전. | GPU 클러스터를 만들 때 배포. 단일 GPU Node Ready 확인. |
| B2 | `gpu-services/inject-aisrc.sh` | 아래 명령의 관리 context, archive 경로, SSH 키 경로. | GPU 이름 `demo-gpu-a`, namespace `default`. | B1 이후 관리 호스트에서 1회 실행. `AISRC_TRANSFER_READY` 확인. |
| B3 | `infra/capa-free5gc/gpu-services` | **기본 환경이면 수정 없음.** 카탈로그 이름·브랜치를 바꿨을 때만 `catalog-name`, `catalog-revision` 변경. | `gpu-cluster-name: demo-gpu-a`, `staging-repository: mgmt-staging`. | B2 이후 배포. 모델·캐시·FaaS·GPU API가 자동 준비됨. |
| B4 | `infra/capa-free5gc/gpu-bindings` | **기본 환경이면 수정 없음.** | `edge-cluster-name: edge`, `gpu-cluster-name: demo-gpu-a`, `namespace: default`. | B3 게시 후 배포. GPU API·Edge API 준비를 기다린 뒤 자동 연결. |

### B1: 바꿀 값

`infra/capa-free5gc/gpu-cluster/setters.yaml`의 `data`에서 다음 값을 실제 환경에 맞춘다. VPC와 공개 subnet은 Core·Edge와 함께 준비한 AWS 리소스를 사용한다.

```yaml
  vpc-id: vpc-0123456789abcdef0
  public-subnet-id: subnet-0123456789abcdef0
  ssh-key-name: mynephio2025
```

GPU 기본 NIC에는 별도의 고정 ENI가 필요하지 않다. 공개 IP 할당·드라이버·런타임·단일 노드 Kubernetes·Flannel은 B1에서 처리한다.

### B2: AISRC 파일 전달

관리 클러스터에 접속하는 kubeconfig가 있는 호스트에서 저장소 루트를 기준으로 실행한다. `--context`에는 해당 kubeconfig의 관리 context 이름을 입력한다.

```bash
bash infra/capa-free5gc/gpu-services/inject-aisrc.sh \
  --context kubernetes-admin@kubernetes \
  --namespace default \
  --cluster demo-gpu-a \
  --archive "$HOME/voice-studio-platform-internal-20261030.tar.gz" \
  --ssh-key "$HOME/mynephio2025.pem"
```

GPU 공개 IP는 스크립트가 조회한다. archive의 `voice-studio-platform/private/aisrc/`에서 다음 파일을 추출해 GPU 노드의 `/var/lib/voice-private/aisrc/`에 전송한다.

| 전달 내용 | archive 내부 경로 |
|---|---|
| 앱 이미지 | `image.tar`. |
| 암호화 모델 | `runtime/pretrained/`. |
| 앱 설정·인증 | `runtime/client.env`, `runtime/DATA/license/`, `runtime/DATA/security/`, `machine-id`. |

정상 출력은 `AISRC_INPUT_READY` → `AISRC_TRANSFER_READY`다. 이후 B3에서 이미지 적재·인증 주입을 자동 수행한다.

### B3·B4: 기본값 그대로 배포

B3는 `00-namespaces`~`40-faas` 하위 패키지를 자동 전달하고, 다운로드·모델 준비·RAM 캐시·KService·GPU API를 구성한다. 하위 패키지를 하나씩 배포하지 않는다.

B4는 GPU 공개 API 주소·토큰을 Edge에 자동 전달한다. GPU 주소나 토큰을 Core·Edge `setters.yaml`에 입력하지 않는다. Edge 서비스 패키지는 이 작업과 병렬로 게시할 수 있다.

## 3. 완료 확인

| 위치 | 정상 상태 |
|---|---|
| 관리 클러스터 | `demo-gpu-a` Cluster 준비, `ims-gpu-bindings` Deployment Ready. |
| GPU 클러스터 | 단일 Node Ready, 모델 준비 Job Complete. |
| GPU 서비스 | `sasv-restored`, `voice-ims-fast` KService Ready, `voice-gpu-api` Deployment `1/1`. |
| 전화 데모 | 송신 UE가 생성 WAV를 수신하고 통화로 송출. 수신자의 판별 요청에 결과 반환. |
| 인프라 관측 | 요청에 따른 판별 Pod `0→1→2→0`. |

```bash
# 관리 클러스터
kubectl -n default get cluster demo-gpu-a
kubectl -n default get deployment ims-gpu-bindings

# 준비된 GPU kubeconfig로 확인
kubectl --kubeconfig gpu.kubeconfig get nodes
kubectl --kubeconfig gpu.kubeconfig get ksvc -A
kubectl --kubeconfig gpu.kubeconfig -n voice-system get deployment voice-gpu-api
```

모델 Pod가 유휴 상태에서 0개여도 KService는 Ready를 유지한다. GPU 노드를 재부팅하면 저장된 원본에서 RAM 캐시를 자동으로 다시 준비한다.
