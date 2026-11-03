#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole node-viewer >/dev/null
kubectl -n arch-crb get sa node-inspector >/dev/null
kubectl get clusterrolebinding node-viewer-binding >/dev/null
VERBS=$(kubectl get clusterrole node-viewer -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
echo "$VERBS" | grep -q watch
RES=$(kubectl get clusterrole node-viewer -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q nodes
REF=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "node-viewer" ]
SUB=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "node-inspector" ]
KIND=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.subjects[0].kind}')
[ "$KIND" = "ServiceAccount" ]
NS=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.subjects[0].namespace}')
[ "$NS" = "arch-crb" ]
exit 0
