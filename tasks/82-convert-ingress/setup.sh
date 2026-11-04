#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-ing82 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-ing82 create deploy echo --image=nginx:1.27
kubectl -n net-ing82 expose deploy echo --port=80
kubectl -n net-ing82 apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: echo-ing
  namespace: net-ing82
spec:
  ingressClassName: nginx
  rules:
    - host: echo.cka.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: echo
                port:
                  number: 80
EOF
kubectl -n net-ing82 rollout status deploy/echo --timeout=120s
