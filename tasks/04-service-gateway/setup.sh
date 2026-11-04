#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-lab --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-lab apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello
  namespace: net-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:
        - name: hello
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
EOF
kubectl -n net-lab rollout status deploy/hello --timeout=180s
