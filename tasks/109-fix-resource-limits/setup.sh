#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-res109 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-res109 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: heavy
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    resources:
      requests:
        cpu: "64"
        memory: 128Mi
EOF
