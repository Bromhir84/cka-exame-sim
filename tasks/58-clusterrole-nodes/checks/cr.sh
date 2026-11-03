#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole node-inspector >/dev/null
RES=$(kubectl get clusterrole node-inspector -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q nodes
VERBS=$(kubectl get clusterrole node-inspector -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
exit 0
