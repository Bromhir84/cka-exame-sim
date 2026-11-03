#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-multiport --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-multiport apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dual
  namespace: net-multiport
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dual
  template:
    metadata:
      labels:
        app: dual
    spec:
      containers:
        - name: dual
          image: hashicorp/http-echo:1.0
          args: ["-text=dual","-listen=:80"]
          ports:
            - containerPort: 80
            - containerPort: 8080
EOF
kubectl -n net-multiport rollout status deploy/dual --timeout=120s
