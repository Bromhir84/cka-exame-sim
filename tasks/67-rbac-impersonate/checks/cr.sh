#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl get clusterrole user-impersonator -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q users
VERBS=$(kubectl get clusterrole user-impersonator -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q impersonate
exit 0
