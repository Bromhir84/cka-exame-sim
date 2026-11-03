#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-egress --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-egress apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: client
  namespace: net-egress
  labels:
    app: client
spec:
  containers:
    - name: c
      image: busybox:1.36
      command: ["sleep","3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: api
  namespace: net-egress
  labels:
    app: api
spec:
  containers:
    - name: a
      image: busybox:1.36
      command: ["sleep","3600"]
EOF
kubectl -n net-egress wait --for=condition=Ready pod/client pod/api --timeout=120s
