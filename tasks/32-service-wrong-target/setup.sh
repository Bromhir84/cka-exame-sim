#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-target --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-target apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  namespace: ts-target
spec:
  replicas: 1
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      containers:
        - name: echo
          image: hashicorp/http-echo:1.0
          args: ["-text=ok","-listen=:8080"]
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: echo-svc
  namespace: ts-target
spec:
  selector:
    app: echo
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-target rollout status deploy/echo --timeout=120s
