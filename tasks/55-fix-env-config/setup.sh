#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-env --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-env apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
  namespace: ts-env
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
          command: ["sh","-c","test -n \"$MODE\" && sleep 3600"]
          env:
            - name: MODE
              valueFrom:
                configMapKeyRef:
                  name: worker-config
                  key: MODE
EOF
