#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-port106 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-port106 create deploy web --image=nginx:1.27
kubectl -n ts-port106 expose deploy web --port=80 --target-port=8080
kubectl -n ts-port106 rollout status deploy/web --timeout=120s
