#!/usr/bin/env bash
set -euo pipefail

NS=rbac-lab
kubectl -n "$NS" get sa deployer >/dev/null
kubectl -n "$NS" get role deployer-role >/dev/null
kubectl -n "$NS" get rolebinding deployer-binding >/dev/null

# Role must cover pods and deployments with required verbs
ROLE_JSON=$(kubectl -n "$NS" get role deployer-role -o json)
echo "$ROLE_JSON" | grep -q '"pods"'
echo "$ROLE_JSON" | grep -q '"deployments"'
for v in get list watch create update delete; do
  echo "$ROLE_JSON" | grep -q "\"$v\""
done

# Binding must reference SA and Role
RB_JSON=$(kubectl -n "$NS" get rolebinding deployer-binding -o json)
echo "$RB_JSON" | grep -q '"deployer-role"'
echo "$RB_JSON" | grep -q '"deployer"'
echo "$RB_JSON" | grep -q '"ServiceAccount"'

exit 0
