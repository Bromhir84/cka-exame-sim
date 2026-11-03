#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-lab111 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-lab111 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: www}
    spec:
      containers:
      - name: web
        image: nginx:1.27
EOF
# This apply may fail validation — use create then broken? selector must match template.
# Use valid deploy then relabel service instead:
kubectl -n ts-lab111 delete deploy web --ignore-not-found
kubectl -n ts-lab111 create deploy web --image=nginx:1.27
kubectl -n ts-lab111 expose deploy web --port=80
kubectl -n ts-lab111 label deploy web app=web --overwrite
# Break: change service selector
kubectl -n ts-lab111 patch svc web -p '{"spec":{"selector":{"app":"www"}}}'
kubectl -n ts-lab111 rollout status deploy/web --timeout=120s
