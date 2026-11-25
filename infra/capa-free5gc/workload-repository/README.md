# 전화 데모 blueprint 카탈로그

관리 클러스터에 배포하는 KPT 패키지다. `setters.yaml`의 Git URL·브랜치·namespace를 설정하면 Porch Repository `catalog-ims-demo`를 등록한다. 이 Repository는 원형 패키지 카탈로그이며 워크로드를 직접 실행하지 않는다.

Core·Edge 패키지는 카탈로그에서 각 클러스터의 Repository로 복제·설정·게시한다. GPU 서비스는 관리 클러스터의 `gpu-services`가 하위 패키지를 `mgmt-staging`에 게시한다. [서비스 설치 절차](../../../free5gc-ims/docs/INSTALL.md)를 따른다.
