# GPU 서비스 배포

관리 클러스터에 배포하는 KPT 패키지다. `setters.yaml`의 GPU 클러스터 이름·관리 namespace·카탈로그 revision을 입력해 Porch에 게시한다.

- `00-namespaces.yaml` ~ `40-faas.yaml`: GPU 하위 패키지를 `mgmt-staging`에 복제·게시하는 PackageVariant.
- `nephio.org/cluster-name`: Nephio가 전달할 GPU 클러스터 이름.
- `inject-aisrc.sh`: B2에서 관리 클러스터 호스트가 실행하는 비공개 파일 전송 스크립트.

다운로드·파일 설치·장치 준비는 캡처 Job이 내부에서 확인한다. 하위 패키지 사이에 수동 대기 명령을 넣지 않는다. 설치 절차와 예상 출력은 [GPU 설치 문서](../../../free5gc-ims/gpu/README.md)에 있다.
