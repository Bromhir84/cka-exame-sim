#!/usr/bin/env bash
set -euo pipefail
NS=ts-pending
IMG=$(kubectl -n "$NS" get pod stuck -o jsonpath='{.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n "$NS" wait --for=condition=Ready pod/stuck --timeout=120s
exit 0
