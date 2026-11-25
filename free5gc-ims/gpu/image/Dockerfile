FROM ubuntu:24.04@sha256:24737cef17f4e22b1977df7d9a05e77c4e28b7da5b8911f8d8ccda136bf3573c
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 NVIDIA_VISIBLE_DEVICES=all NVIDIA_DRIVER_CAPABILITIES=utility
RUN sed -i -E 's#http://(archive|security).ubuntu.com/ubuntu/#http://ap-northeast-2.ec2.archive.ubuntu.com/ubuntu/#g' /etc/apt/sources.list.d/ubuntu.sources && apt-get -o Acquire::ForceIPv4=true update && apt-get -o Acquire::ForceIPv4=true install -y --no-install-recommends python3 python3-venv python3-pip ca-certificates curl ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt quality_requirements.txt /tmp/
RUN python3 -m venv /opt/voice-api/runtime && /opt/voice-api/runtime/bin/pip install --no-cache-dir -r /tmp/requirements.txt && python3 -m venv /opt/voice-quality/runtime && /opt/voice-quality/runtime/bin/pip install --no-cache-dir -r /tmp/quality_requirements.txt
ARG KUBECTL_VERSION=v1.33.13
RUN curl -fsSL https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl -o /usr/local/bin/kubectl && curl -fsSL https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256 -o /tmp/kubectl.sha256 && printf '%s  %s\n' "$(cat /tmp/kubectl.sha256)" /usr/local/bin/kubectl | sha256sum -c - && chmod 0755 /usr/local/bin/kubectl
WORKDIR /app
CMD ["/opt/voice-api/runtime/bin/uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8090", "--no-access-log"]
