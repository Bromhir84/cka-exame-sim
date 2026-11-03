#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-probe --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-probe apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: ts-probe
spec:
  replicas: 2
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
          readinessProbe:
            httpGet:
              path: /this-path-does-not-exist
              port: 80
            initialDelaySeconds: 1
            periodSeconds: 3
EOF
sleep 3
