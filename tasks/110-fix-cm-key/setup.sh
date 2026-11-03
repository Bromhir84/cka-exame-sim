#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-cm110 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-cm110 create cm app-cm --from-literal=config=hello
kubectl -n ts-cm110 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: need-cm
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    env:
    - name: APP
      valueFrom:
        configMapKeyRef:
          name: app-cm
          key: app.conf
EOF
