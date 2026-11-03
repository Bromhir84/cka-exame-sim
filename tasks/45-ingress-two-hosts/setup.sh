#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-twohost --dry-run=client -o yaml | kubectl apply -f -
for name in alpha beta; do
  kubectl -n net-twohost create deploy "$name" --image=nginx:1.27
  kubectl -n net-twohost expose deploy "$name" --name="${name}-svc" --port=80
  kubectl -n net-twohost rollout status deploy/"$name" --timeout=120s
done
