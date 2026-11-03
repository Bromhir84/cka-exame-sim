#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace policy-lab --dry-run=client -o yaml | kubectl apply -f -
kubectl -n policy-lab apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: secure-db
  namespace: policy-lab
  labels:
    app: secure-db
spec:
  containers:
    - name: db
      image: busybox:1.36
      command: ["sleep", "3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: frontend
  namespace: policy-lab
  labels:
    role: frontend
spec:
  containers:
    - name: fe
      image: busybox:1.36
      command: ["sleep", "3600"]
EOF
kubectl -n policy-lab wait --for=condition=Ready pod/secure-db pod/frontend --timeout=120s
