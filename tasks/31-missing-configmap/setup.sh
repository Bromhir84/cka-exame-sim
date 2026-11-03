#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-cm --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-cm apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cfg-app
  namespace: ts-cm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cfg-app
  template:
    metadata:
      labels:
        app: cfg-app
    spec:
      containers:
        - name: app
          image: nginx:1.27
          volumeMounts:
            - name: cfg
              mountPath: /etc/cfg
      volumes:
        - name: cfg
          configMap:
            name: app-settings
EOF
sleep 2
