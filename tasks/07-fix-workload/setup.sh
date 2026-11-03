#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace broken-app --dry-run=client -o yaml | kubectl apply -f -
kubectl -n broken-app apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: broken-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: nginx:1.27-this-tag-does-not-exist
          ports:
            - containerPort: 80
EOF
# Give it a moment to show failures; don't wait for Ready
sleep 2
