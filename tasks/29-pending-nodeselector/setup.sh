#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-pending --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-pending apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: stuck
  namespace: ts-pending
spec:
  nodeSelector:
    disktype: not-a-real-label-xyz
  containers:
    - name: web
      image: nginx:1.27
EOF
