#!/usr/bin/env bash
set -euo pipefail
HOSTS=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.rules[*].host}')
echo "$HOSTS" | grep -q alpha.cka.local
echo "$HOSTS" | grep -q beta.cka.local
exit 0
