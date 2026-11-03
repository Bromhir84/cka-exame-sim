#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-selector --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-selector apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ts-selector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: nginx:1.27
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: backend-svc
  namespace: ts-selector
spec:
  selector:
    app: backend-WRONG
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-selector rollout status deploy/backend --timeout=120s
