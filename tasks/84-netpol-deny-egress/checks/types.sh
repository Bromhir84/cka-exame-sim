#!/usr/bin/env bash
set -euo pipefail
T=$(kubectl -n net-eg84 get networkpolicy deny-egress -o jsonpath='{.spec.policyTypes[*]}')
echo "$T" | grep -q Egress
exit 0
