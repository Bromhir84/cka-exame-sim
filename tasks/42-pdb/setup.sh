#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-pdb --dry-run=client -o yaml | kubectl apply -f -
kubectl -n wl-pdb apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: wl-pdb
spec:
  replicas: 2
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
        - name: api
          image: nginx:1.27
EOF
kubectl -n wl-pdb rollout status deploy/api --timeout=120s
