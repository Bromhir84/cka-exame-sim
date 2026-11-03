#!/usr/bin/env bash
set -euo pipefail
NS=ts-probe
PATHP=$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}')
[ "$PATHP" = "/" ]
kubectl -n "$NS" rollout status deploy/web --timeout=120s
READY=$(kubectl -n "$NS" get deploy web -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "2" ]
exit 0
