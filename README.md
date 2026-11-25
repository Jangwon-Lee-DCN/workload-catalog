# 전화 데모 배포 패키지

| 경로 | 배포 대상 | 내용 |
|---|---|---|
| [infra/capa-free5gc](infra/capa-free5gc/README.md) | 관리 클러스터 | ENI controller·ENIPool, Core·Edge CAPA, Nephio bootstrap·ArgoCD 연결. |
| [free5gc-ims/core](free5gc-ims/docs/INSTALL.md) | Core 클러스터 | free5GC 제어부·IMS·가입자 등록. |
| [free5gc-ims/edge](free5gc-ims/docs/INSTALL.md) | Edge 클러스터 | UPF·gNB·UE 전화 앱·RTPengine·MEC 검사·실시간 관측. |
| [cluster-bindings](infra/capa-free5gc/cluster-bindings/Kptfile) | 관리 클러스터 | Core API 주소·관측 자격 정보를 Edge에 자동 전달. |
| [gpu-cluster](infra/capa-free5gc/gpu-cluster/Kptfile) | 관리 클러스터 | 공개 Ubuntu 24.04 CAPA 이미지 기반 단일 GPU CAPA 클러스터. |
| [gpu-bindings](infra/capa-free5gc/gpu-bindings/Kptfile) | 관리 클러스터 | GPU 공개 API 주소·접속 토큰을 Edge에 자동 전달. |
| [workload-repository](infra/capa-free5gc/workload-repository/Kptfile) | 관리 클러스터 | Porch 원형 패키지 카탈로그 등록. |
| [gpu-services](infra/capa-free5gc/gpu-services/Kptfile) | 관리 클러스터 | GPU 하위 패키지를 Porch·Nephio로 자동 전달. |
| [free5gc-ims/gpu](free5gc-ims/gpu/README.md) | GPU 클러스터 | 공개 Ubuntu 24.04 CAPA 이미지 기반 FaaS 판별·음성 생성 서비스. |

전체 순서와 병렬 실행 구간은 [패키지 배포 다이어그램](infra/capa-free5gc/docs/INSTALL.md#1-패키지-배포-순서)에 있다. AISRC 파일 주입 위치도 포함한다. GPU 공개 주소·접속 토큰은 연결 패키지가 Edge에 자동 전달한다.

CPU 앱 코드·웹 파일·GPU API 코드는 배포 ConfigMap에 포함된다. 공개 실행 이미지는 Docker Hub의 고정 digest를 사용한다. GPU 복원 런타임은 사전 빌드 바이너리 이미지, AISRC 앱·모델·인증은 별도 파일로 제공한다. 설치자가 이미지를 빌드하거나 모델 UID를 수동 입력하지 않는다.
