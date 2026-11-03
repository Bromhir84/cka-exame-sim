#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-svclabel --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-svclabel apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fe
  namespace: net-svclabel
spec:
  replicas: 1
  selector:
    matchLabels:
      tier: frontend
      env: prod
  template:
    metadata:
      labels:
        tier: frontend
        env: prod
    spec:
      containers:
        - name: fe
          image: nginx:1.27
          ports:
            - containerPort: 80
EOF
kubectl -n net-svclabel rollout status deploy/fe --timeout=120s
