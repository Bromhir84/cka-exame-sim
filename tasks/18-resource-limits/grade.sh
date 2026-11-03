#!/usr/bin/env bash
set -euo pipefail
NS=wl-limits
RC=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')
RM=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')
LC=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.cpu}')
LM=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.memory}')
[ "$RC" = "50m" ]
[ "$RM" = "32Mi" ]
[ "$LC" = "200m" ]
[ "$LM" = "128Mi" ]
kubectl -n "$NS" rollout status deploy/limited --timeout=120s
exit 0
