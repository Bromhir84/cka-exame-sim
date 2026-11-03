#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-headless --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-headless apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stateful-like
  namespace: net-headless
spec:
  replicas: 2
  selector:
    matchLabels: {app: store}
  template:
    metadata:
      labels: {app: store}
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
EOF
kubectl -n net-headless rollout status deploy/stateful-like --timeout=120s
