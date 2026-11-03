#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-tls86 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-tls86 create deploy web --image=nginx:1.27
kubectl -n net-tls86 expose deploy web --port=80
kubectl -n net-tls86 rollout status deploy/web --timeout=120s
