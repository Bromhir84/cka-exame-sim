#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-svc103 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-svc103 create deploy web --image=nginx:1.27
kubectl -n ts-svc103 expose deploy web --port=80
kubectl -n ts-svc103 label deploy web app=web --overwrite
kubectl -n ts-svc103 patch svc web -p '{"spec":{"selector":{"app":"website"}}}'
kubectl -n ts-svc103 rollout status deploy/web --timeout=120s
