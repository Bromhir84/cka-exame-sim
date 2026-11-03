#!/usr/bin/env bash
set -euo pipefail
NS=arch-svc-rbac
kubectl -n "$NS" get sa svc-manager >/dev/null
kubectl -n "$NS" get role svc-manager-role -o jsonpath='{.rules[0].resources[*]}' | grep -q services
for v in get list create delete; do
  kubectl -n "$NS" get role svc-manager-role -o jsonpath='{.rules[0].verbs[*]}' | grep -q "$v"
done
kubectl -n "$NS" get rolebinding svc-manager-binding >/dev/null
exit 0
