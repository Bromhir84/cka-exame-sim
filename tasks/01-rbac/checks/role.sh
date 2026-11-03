#!/usr/bin/env bash
set -euo pipefail

NS=rbac-lab
kubectl -n "$NS" get role deployer-role >/dev/null
ROLE_JSON=$(kubectl -n "$NS" get role deployer-role -o json)
echo "$ROLE_JSON" | grep -q '"pods"'
echo "$ROLE_JSON" | grep -q '"deployments"'
for v in get list watch create update delete; do echo "$ROLE_JSON" | grep -q "\"$v\""; done
