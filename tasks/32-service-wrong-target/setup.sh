#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-target --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-target apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  namespace: ts-target
spec:
  replicas: 1
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      containers:
        - name: echo
          image: nginx:1.27
          command: ["/bin/sh", "-c"]
          args:
            - |
              printf '%s\n' 'server { listen 8080; location / { root /usr/share/nginx/html; } }' > /etc/nginx/conf.d/default.conf
              nginx -g 'daemon off;'
          ports:
            - containerPort: 8080
          readinessProbe:
            tcpSocket:
              port: 8080
            initialDelaySeconds: 2
            periodSeconds: 3
---
apiVersion: v1
kind: Service
metadata:
  name: echo-svc
  namespace: ts-target
spec:
  selector:
    app: echo
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-target rollout status deploy/echo --timeout=180s
