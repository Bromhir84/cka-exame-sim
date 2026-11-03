#!/usr/bin/env bash
set -euo pipefail

NS=workloads-lab
kubectl -n "$NS" rollout status deploy/web --timeout=120s
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.status.readyReplicas}')" = "3" ]
