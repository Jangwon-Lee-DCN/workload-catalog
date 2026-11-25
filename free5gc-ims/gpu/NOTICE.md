# 공개 입력·비공개 입력

| 입력 | 출처·범위 |
|---|---|
| Knative Serving 1.21.0 | https://github.com/knative/serving · CRD·Serving 리소스. Apache-2.0. |
| Kourier 1.21.0 | https://github.com/knative-extensions/net-kourier · 네트워크 리소스. Apache-2.0. |
| NVIDIA k8s-device-plugin | https://github.com/NVIDIA/k8s-device-plugin · time-slicing 공유 슬롯. Apache-2.0. |
| Qwen3-TTS | https://github.com/QwenLM/Qwen3-TTS · qwen-tts 0.1.1, Base 모델. |
| metrics-server 0.8.1 | https://github.com/kubernetes-sigs/metrics-server · Kubernetes 1.33의 CPU HPA 지표 제공. Apache-2.0. |
| CPU STT | https://github.com/SYSTRAN/faster-whisper · 공개 모델의 문장 확인. |
| pybase64 | https://github.com/mayeut/pybase64 · 공개 네이티브 디코더 wheel. BSD-2-Clause. |
| Python 표준 라이브러리 | CPython base64·torch 연계 wrapper의 원래 고지 유지. Python Software Foundation License. |
| Fake Voice Detection (Source: AISRC) | 이미지·가중치·라이선스는 별도 전달 파일. 이 저장소는 재배포하지 않음. |
| GPU 복원 런타임 | 고정된 바이너리 배포 이미지에서 설치. 복원 구현 원본·패치·빌드 입력은 저장소에 포함하지 않음. |

공개 입력의 버전·이미지 digest와 패키지 파일 정보는 `source-lock.json`에 기록한다. 공개 ConfigMap의 `pybase64.whl`은 위 공개 라이브러리이며, GPU 복원 바이너리가 아니다. `private/`, 렌더링 결과와 생성 Secret은 Git에서 제외한다.

`voice-cache-code`는 제공된 CPU/GPU 상태 파일을 RAM에 미리 복사·전개하는 배포 코드다. 체크포인트 생성·프로세스/GPU 복원 구현은 사전 빌드 런타임 바이너리에 있다.
