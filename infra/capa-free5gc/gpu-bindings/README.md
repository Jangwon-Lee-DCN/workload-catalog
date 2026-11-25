# GPU·Edge 연결 패키지

관리 클러스터에서 CAPA가 생성한 두 클러스터의 kubeconfig Secret을 읽는다. GPU API가 준비되면 공개 주소와 생성된 접속 토큰을 Edge의 `ims-generation-gpu` Secret으로 전달한다.

| 설정 | 기본값 |
|---|---|
| `namespace` | `default`: CAPA 리소스·kubeconfig Secret 위치. |
| `gpu-cluster-name` | `demo-gpu-a`. |
| `edge-cluster-name` | `edge`. |
| `edge-namespaces` | `ims-lab,free5gc`: 전화 앱·MEC와 UPF 설정. |

Secret에는 `gpu-api`, `gpu-ip`, `gpu-token`이 들어간다. API 주소는 AWSMachine의 ExternalIP에서 읽으며 사설 주소로 대체하지 않는다. 값이 변경되면 Secret을 갱신하고 삭제된 Secret을 복구한다. UE·MEC·관측 서비스는 요청 시 마운트된 Secret 파일을 읽고, UPF는 IP 변경 시 경로를 갱신한다. Secret 갱신이 볼륨에 반영되면 Pod 재생성 없이 새 주소·토큰을 사용한다.

배포 명령은 [GPU·FaaS 설치 순서](../../../free5gc-ims/gpu/README.md)의 4절을 따른다. 연결 토큰을 setters나 Git에 넣지 않는다.
