#!/usr/bin/env bash
set -euo pipefail

NS=broken-app
IMAGE=$(kubectl -n "$NS" get deploy frontend -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMAGE" = "nginx:1.27" ]
kubectl -n "$NS" rollout status deploy/frontend --timeout=120s
READY=$(kubectl -n "$NS" get deploy frontend -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "2" ]

exit 0
