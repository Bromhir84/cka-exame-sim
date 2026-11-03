#!/usr/bin/env bash
set -euo pipefail
NS=wl-scale
REP=$(kubectl -n "$NS" get deploy api -o jsonpath='{.spec.replicas}')
[ "$REP" = "4" ]
kubectl -n "$NS" rollout status deploy/api --timeout=120s
READY=$(kubectl -n "$NS" get deploy api -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "4" ]
exit 0
