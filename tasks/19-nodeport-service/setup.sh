#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-nodeport --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-nodeport apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: net-nodeport
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
EOF
kubectl -n net-nodeport rollout status deploy/web --timeout=120s
