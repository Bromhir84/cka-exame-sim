#!/usr/bin/env bash
set -euo pipefail
NS=arch-secrets
kubectl -n "$NS" get sa secret-reader >/dev/null
kubectl -n "$NS" get role secret-reader-role >/dev/null
kubectl -n "$NS" get rolebinding secret-reader-binding >/dev/null
RES=$(kubectl -n "$NS" get role secret-reader-role -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q secrets
for v in get list watch; do
  kubectl -n "$NS" get role secret-reader-role -o jsonpath='{.rules[0].verbs[*]}' | grep -q "$v"
done
exit 0
