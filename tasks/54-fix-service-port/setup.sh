#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-port --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-port apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: ts-port
spec:
  replicas: 1
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
        - name: api
          image: hashicorp/http-echo:1.0
          args: ["-text=ok", "-listen=:8080"]
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api-svc
  namespace: ts-port
spec:
  selector: {app: api}
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-port rollout status deploy/api --timeout=180s
