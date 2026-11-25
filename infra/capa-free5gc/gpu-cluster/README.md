# 단일 GPU CAPA 패키지

관리 클러스터에 적용하는 단일 GPU 노드 blueprint다. [GPU·FaaS 설치 순서](../../../free5gc-ims/gpu/README.md)에 따라 배포한다.

| 리소스 | 역할 |
|---|---|
| AWSCluster | 기존 VPC·공개 서브넷 사용, API NLB·GPU API 접근 구성. |
| AWSMachineTemplate | 공개 Ubuntu 24.04 CAPA 이미지, g6.8xlarge, Public IPv4, gp3 400 GiB. |
| KubeadmControlPlane | 단일 GPU 노드, 드라이버·Toolkit 준비, 사전 빌드 복원 바이너리 설치. |
| Cluster | CAPA 클러스터 연결. |
| WorkloadCluster·PackageVariant | Nephio mgmt-staging 방식으로 Flannel 배포. |

`setters.yaml`에서 namespace·클러스터 이름·VPC·공개 서브넷·AZ·AMI·SSH 키를 설정한다. AISRC 파일은 별도로 주입한다. 이 패키지는 모델을 설치하지 않는다.
