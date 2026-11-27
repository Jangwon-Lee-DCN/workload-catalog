# 환경 값

각 `core`, `edge` 패키지의 `setters.yaml`에서 `data` 값을 입력한다. 모든 값은 문자열이며 아래 값은 입력 형태를 보여 주는 예시다.

| 키 | 예시 | 설정·획득 방법 |
|---|---|---|
| `core-worker-ip` | `172.31.81.10` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `edge-worker-ip` | `172.31.81.11` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `core-node-name` | `ip-172-31-81-10.ap-northeast-2.compute.internal` | `kubectl --context core/edge get nodes`의 NAME. |
| `edge-node-name` | `ip-172-31-81-11.ap-northeast-2.compute.internal` | `kubectl --context core/edge get nodes`의 NAME. |
| `ims-domain` | `ims.mnc001.mcc001.3gppnetwork.org` | 두 클러스터의 IMS DNS·인증 realm에 동일 적용. PLMN 변경 시 전체 가입자·free5GC 설정도 함께 변경. |
| `ims-domain-regex` | `ims\.mnc001\.mcc001\.3gppnetwork\.org` | KPT 렌더링 함수가 도메인/IP에서 계산. |
| `pcscf-ip` | `172.31.93.210` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `rtpengine-ip` | `172.31.93.211` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `mec-ip` | `172.31.93.213` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `upf-n6-ip` | `172.31.93.203` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `amf-n2-ip` | `172.31.90.200` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `smf-n4-ip` | `172.31.91.176` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `upf-n4-ip` | `172.31.91.202` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `upf-n3-ip` | `172.31.92.201` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `gnb-n2-ip` | `172.31.90.204` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `gnb-n3-ip` | `172.31.92.205` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `n2-gateway` | `172.31.90.1` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `n4-gateway` | `172.31.91.1` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `n3-gateway` | `172.31.92.1` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `n6-gateway` | `172.31.93.1` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `n6-cidr` | `172.31.93.0/24` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `ue-cidr` | `10.1.0.0/16` | VPC subnet/ENI Secondary private IPv4와 NAD 주소에 일치시킴. GPU IP는 선택적 외부 연동 주소. |
| `n2-master` | `ens6` | 해당 worker의 `ip -br addr`로 NIC 이름 확인. |
| `n4-master` | `ens7` | 해당 worker의 `ip -br addr`로 NIC 이름 확인. |
| `n3-master` | `ens8` | 해당 worker의 `ip -br addr`로 NIC 이름 확인. |
| `n6-master` | `ens9` | 해당 worker의 `ip -br addr`로 NIC 이름 확인. |
| `storage-class` | `standard` | `kubectl --context core get storageclass`의 이름. |
| `dns-upstream` | `169.254.169.253` | Core worker에서 접근 가능한 DNS resolver. 예시는 AWS VPC Resolver. |
| `mysql-password` | `password` | 데모 기본값 유지. Core·Edge에서 같은 값 사용. |
| `kamailio-password` | `password` | 데모 기본값 유지. Core·Edge에서 같은 값 사용. |
| `hss-password` | `password` | 데모 기본값 유지. Core·Edge에서 같은 값 사용. |
| `ue-1-key` | `00112233445566778899aabbccddeeff` | 설치자가 32자리 hex 입력. 5GC·IMS·UE에 같은 값으로 배포. |
| `ue-1-opc` | `ffeeddccbbaa99887766554433221100` | 설치자가 32자리 hex 입력. 5GC·IMS·UE에 같은 값으로 배포. |
| `ue-2-key` | `102132435465768798a9bacbdcedfe0f` | 설치자가 32자리 hex 입력. 5GC·IMS·UE에 같은 값으로 배포. |
| `ue-2-opc` | `0ffedccba98765432100123456789abc` | 설치자가 32자리 hex 입력. 5GC·IMS·UE에 같은 값으로 배포. |
| `mec-key` | `11223344556677889900aabbccddeeff` | 설치자가 32자리 hex 입력. 5GC·IMS·UE에 같은 값으로 배포. |
| `mec-opc` | `ffeeddccbbaa00998877665544332211` | 설치자가 32자리 hex 입력. 5GC·IMS·UE에 같은 값으로 배포. |
| `generation-auth-token` | `password` | 데모 기본값 유지. Core·Edge에서 같은 값 사용. |
| `generation-provider` | `gpu_local` | `gpu_local`, `hf_public`, `elevenlabs` 중 선택. |
| `generation-enabled` | `true` | 기본 활성화. 두 UE가 GPU 노드의 생성 API를 호출. |
| `inspection-enabled` | `true` | GPU 연결 패키지가 전달한 API로 판별. |
| `phone-hostname` | `voice.3.38.223.206.sslip.io` | 공개 EIP를 가리키는 접속 DNS 이름. 공개 HTTPS 인증서에 사용. |
| `public-service-name` | `ims-public-gateway` | AWS CCM이 NLB를 생성할 LoadBalancer Service 이름. |
| `public-subnet-id` | `subnet-0123456789abcdef0` | Edge VPC의 IGW 연결 공개 서브넷 ID. |
| `public-eip-allocation-id` | `eipalloc-0123456789abcdef0` | 위 DNS 주소에 대응하는 미연결 EIP Allocation ID. |
| `public-source-cidrs` | `0.0.0.0/0` | 공개 웹 화면의 접근 허용 CIDR. 기본값은 전체 IPv4 허용. 여러 대역은 쉼표로 구분. |
| `tls-issuer-name` | `ims-phone-selfsigned` | Edge HTTPS 인증서 발급자. 기본값 유지. |
| `tls-issuer-kind` | `Issuer` | 기본값 유지. |
| `image-tools` | `docker.io/jangwonlee/ims-demo-runtime@sha256:73f64e0aa6aa164b5603b03ad8d4f33e4ac9991cb8c4e9fd26a2ebe77548ae25` | 기본값 유지. Kubernetes가 공개 Docker Hub에서 자동 다운로드. |
| `image-kamailio` | `ghcr.io/herlesupreeth/docker_kamailio@sha256:6f7c427db924370ba64eb23f27c0d62f50e7856ea10a2205836bdedaf54d31f8` | 실제 pull 가능한 이미지 또는 worker에 적재한 이미지 참조. |
| `image-pyhss` | `ghcr.io/herlesupreeth/docker_pyhss@sha256:ecd1559e12aadbb0a27ece69972b9fa6a897c82e202cac6a054e8d9e2bb8b1fd` | 실제 pull 가능한 이미지 또는 worker에 적재한 이미지 참조. |
| `upf-n6-regex` | `172[.]31[.]93[.]203` | KPT 렌더링 함수가 도메인/IP에서 계산. |
