#!/usr/bin/env bash
set -euo pipefail
NS=arch-sa-deploy
kubectl -n "$NS" get sa app-sa >/dev/null
SA=$(kubectl -n "$NS" get deploy sa-demo -o jsonpath='{.spec.template.spec.serviceAccountName}')
[ "$SA" = "app-sa" ]
IMG=$(kubectl -n "$NS" get deploy sa-demo -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n "$NS" rollout status deploy/sa-demo --timeout=120s
exit 0
