#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-live112 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-live112 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
        image: nginx:1.27
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 3
          periodSeconds: 3
          failureThreshold: 1
EOF
