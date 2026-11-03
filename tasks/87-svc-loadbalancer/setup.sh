#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-lb87 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-lb87 create deploy web --image=nginx:1.27
kubectl -n net-lb87 rollout status deploy/web --timeout=120s
