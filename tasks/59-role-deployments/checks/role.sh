#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-deploy59 get role deploy-manager >/dev/null
RES=$(kubectl -n arch-deploy59 get role deploy-manager -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q deployments
VERBS=$(kubectl -n arch-deploy59 get role deploy-manager -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q create
echo "$VERBS" | grep -q delete
exit 0
