#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-crash --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-crash apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: looper
  namespace: ts-crash
spec:
  replicas: 1
  selector:
    matchLabels:
      app: looper
  template:
    metadata:
      labels:
        app: looper
    spec:
      containers:
        - name: looper
          image: busybox:1.36
          command: ["sh","-c","exit 1"]
EOF
sleep 2
