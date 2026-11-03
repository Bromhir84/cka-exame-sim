#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole node-viewer -o jsonpath="{.rules[0].resources[*]}" | grep -q nodes
kubectl get clusterrole node-viewer -o jsonpath="{.rules[0].verbs[*]}" | grep -q get
