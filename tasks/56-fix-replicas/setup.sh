#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-replicas --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-replicas apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ts-replicas
spec:
  replicas: 0
  selector:
    matchLabels: {app: frontend}
  template:
    metadata:
      labels: {app: frontend}
    spec:
      containers:
        - name: web
          image: nginx:1.27
EOF
