#!/usr/bin/env bash
set -euo pipefail
NS=ts-crash
IMG=$(kubectl -n "$NS" get deploy looper -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
kubectl -n "$NS" rollout status deploy/looper --timeout=120s
READY=$(kubectl -n "$NS" get deploy looper -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "1" ]
exit 0
