FROM python:3.12-slim-bookworm

ARG KUBECTL_VERSION=v1.31.4
ARG KIND_VERSION=v0.26.0
ARG ETCD_VERSION=v3.5.16

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash bash-completion procps util-linux \
    nano vim openssl \
    && command -v nano >/dev/null \
    && command -v vi >/dev/null \
    && command -v vim >/dev/null \
    && command -v openssl >/dev/null \
    && rm -rf /var/lib/apt/lists/*

# kubectl
RUN curl -fsSL "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    -o /usr/local/bin/kubectl \
    && chmod +x /usr/local/bin/kubectl

# kind
RUN curl -fsSL "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-amd64" \
    -o /usr/local/bin/kind \
    && chmod +x /usr/local/bin/kind

# etcdctl
RUN curl -fsSL "https://github.com/etcd-io/etcd/releases/download/${ETCD_VERSION}/etcd-${ETCD_VERSION}-linux-amd64.tar.gz" \
    | tar -xz -C /tmp \
    && mv /tmp/etcd-${ETCD_VERSION}-linux-amd64/etcdctl /usr/local/bin/etcdctl \
    && chmod +x /usr/local/bin/etcdctl \
    && rm -rf /tmp/etcd-${ETCD_VERSION}-linux-amd64

# Docker CLI (talk to mounted socket for kind)
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.3.1.tgz \
    | tar -xz -C /tmp \
    && mv /tmp/docker/docker /usr/local/bin/docker \
    && rm -rf /tmp/docker

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

ENV TASKS_DIR=/app/tasks
ENV SESSIONS_DIR=/var/lib/cka-sessions
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
