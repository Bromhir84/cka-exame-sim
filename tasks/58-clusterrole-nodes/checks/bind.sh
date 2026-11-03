#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-nodes58 get sa node-inspector >/dev/null
kubectl get clusterrolebinding node-inspector-binding >/dev/null
REF=$(kubectl get clusterrolebinding node-inspector-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "node-inspector" ]
SUB=$(kubectl get clusterrolebinding node-inspector-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "node-inspector" ]
exit 0
