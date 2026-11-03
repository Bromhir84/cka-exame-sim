#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-lab --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-lab apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello
  namespace: net-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:
        - name: hello
          image: hashicorp/http-echo:1.0
          args: ["-text=hello-cka", "-listen=:8080"]
          ports:
            - containerPort: 8080
EOF
kubectl -n net-lab rollout status deploy/hello --timeout=120s
