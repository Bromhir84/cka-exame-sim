#!/usr/bin/env bash
set -euo pipefail

NS=rbac-lab
kubectl -n "$NS" get rolebinding deployer-binding >/dev/null
RB_JSON=$(kubectl -n "$NS" get rolebinding deployer-binding -o json)
echo "$RB_JSON" | grep -q '"deployer-role"'
echo "$RB_JSON" | grep -q '"deployer"'
echo "$RB_JSON" | grep -q '"ServiceAccount"'
