#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-deny --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-deny run web --image=nginx:1.27 --labels=app=web --restart=Never
kubectl -n net-deny wait --for=condition=Ready pod/web --timeout=120s
