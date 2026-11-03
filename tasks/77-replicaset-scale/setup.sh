#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-rs77 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n wl-rs77 apply -f - <<'EOF'
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web
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
      - name: nginx
        image: nginx:1.27
EOF
kubectl -n wl-rs77 rollout status replicaset/web --timeout=120s || true
