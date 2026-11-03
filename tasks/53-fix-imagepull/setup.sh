#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-pull --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-pull apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: ts-pull
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
        - name: web
          image: nginx:1.27-this-tag-does-not-exist
EOF
