#!/usr/bin/env bash
set -euo pipefail

NS=policy-lab
[ "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.podSelector.matchLabels.app}')" = "secure-db" ]
echo "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.policyTypes[*]}')" | grep -q Ingress
