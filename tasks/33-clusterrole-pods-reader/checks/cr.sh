#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole pods-reader >/dev/null
VERBS=$(kubectl get clusterrole pods-reader -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
echo "$VERBS" | grep -q watch
RES=$(kubectl get clusterrole pods-reader -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q pods
exit 0
