#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-ready104 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-ready104 apply -f - <<'EOF'
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
        readinessProbe:
          httpGet:
            path: /this-path-does-not-exist
            port: 80
          initialDelaySeconds: 1
          periodSeconds: 3
EOF
