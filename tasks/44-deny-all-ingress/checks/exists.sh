#!/usr/bin/env bash
set -euo pipefail
kubectl -n net-deny get networkpolicy deny-all-ingress >/dev/null
TYPES=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.policyTypes[*]}')
echo "$TYPES" | grep -q Ingress
exit 0
