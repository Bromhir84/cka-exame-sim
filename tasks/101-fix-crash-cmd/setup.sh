#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-crash101 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-crash101 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
spec:
  replicas: 1
  selector:
    matchLabels: {app: worker}
  template:
    metadata:
      labels: {app: worker}
    spec:
      containers:
      - name: worker
        image: busybox:1.36
        command: ["sh","-c","exit 1"]
EOF
