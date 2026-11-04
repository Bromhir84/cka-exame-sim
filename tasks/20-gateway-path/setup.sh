#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-ingpath --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-ingpath apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop
  namespace: net-ingpath
spec:
  replicas: 1
  selector:
    matchLabels:
      app: shop
  template:
    metadata:
      labels:
        app: shop
    spec:
      containers:
        - name: shop
          image: nginx:1.27
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: shop
  namespace: net-ingpath
spec:
  selector:
    app: shop
  ports:
    - port: 80
      targetPort: 80
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: shop-gw
  namespace: net-ingpath
spec:
  gatewayClassName: nginx
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      hostname: shop.cka.local
EOF
kubectl -n net-ingpath rollout status deploy/shop --timeout=120s
