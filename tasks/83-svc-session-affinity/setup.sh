#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-aff83 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-aff83 create deploy web --image=nginx:1.27
kubectl -n net-aff83 label deploy web app=web --overwrite
kubectl -n net-aff83 label pods -l app=web app=web --overwrite 2>/dev/null || true
