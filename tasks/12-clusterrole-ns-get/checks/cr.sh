#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole ns-lister -o jsonpath="{.rules[0].resources[*]}" | grep -q namespaces
kubectl get clusterrole ns-lister -o jsonpath="{.rules[0].verbs[*]}" | grep -q get
