#!/usr/bin/env bash
set -euo pipefail
NS=ts-cm
kubectl -n "$NS" get cm app-settings >/dev/null
MODE=$(kubectl -n "$NS" get cm app-settings -o jsonpath='{.data.mode}')
[ "$MODE" = "online" ]
kubectl -n "$NS" rollout status deploy/cfg-app --timeout=120s
READY=$(kubectl -n "$NS" get deploy cfg-app -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "1" ]
exit 0
