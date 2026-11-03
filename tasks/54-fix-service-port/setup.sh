#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-port --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-port apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: ts-port
spec:
  replicas: 1
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
        - name: api
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
  name: api-svc
  namespace: ts-port
spec:
  selector: {app: api}
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-port rollout status deploy/api --timeout=180s
