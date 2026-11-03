#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-sec105 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-sec105 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: need-secret
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    env:
    - name: CONFIG
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: config
EOF
