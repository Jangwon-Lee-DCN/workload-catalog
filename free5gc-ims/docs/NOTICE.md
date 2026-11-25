# 구성 출처

| 구성 | 프로젝트 | 사용 범위 |
|---|---|---|
| 5GC 제어부·UPF | free5GC | v3.4.3 이미지와 현재 실행 설정. |
| gNB·UE | UERANSIM / free5GC UERANSIM image | 5G 등록·PDU session·UE tunnel. |
| I/P/S-CSCF | Kamailio | IMS 등록·가입자 조회·통화 신호. |
| HSS | PyHSS | IMS AKA 인증·가입자 프로파일. |
| IMS 템플릿·이미지 | herlesupreeth/docker_open5gs | IMS 배치 입력. Open5GS 5GC 구성은 포함하지 않음. |
| 미디어 | Sipwise RTPengine | 통화 RTP 중계와 NG subscribe 복제. |
| 인증서 | cert-manager v1.20.5 | Edge의 인증서·TLS Secret 자동 발급·갱신. Apache-2.0. |
| 전화 앱·MEC 검사·관측 | `edge/50-runtime-code.yaml`의 ConfigMap | SIP MESSAGE 연계·UE 앱·브라우저 UI·외부 GPU API 연결. |

상위 저장소·커밋·관측 이미지 식별자는 `source-lock.json`에 있다. 가져온 upstream 설정 안의 저작권 고지와 별도 라이선스를 유지한다. `docker_open5gs-LICENSE`, `pyhss-LICENSE` 등 제공된 라이선스 파일을 함께 배포한다.

GPU 하위 패키지의 추가 출처·공개 범위는 [GPU 입력 출처](../gpu/NOTICE.md)에 있다.
