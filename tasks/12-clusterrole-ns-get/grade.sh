#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole ns-lister -o jsonpath='{.rules[0].resources[*]}' | grep -q namespaces
kubectl get clusterrole ns-lister -o jsonpath='{.rules[0].verbs[*]}' | grep -q get
kubectl get clusterrole ns-lister -o jsonpath='{.rules[0].verbs[*]}' | grep -q list
kubectl -n arch-ns get sa ns-auditor >/dev/null
kubectl get clusterrolebinding ns-lister-binding -o jsonpath='{.roleRef.name}' | grep -qx ns-lister
exit 0
