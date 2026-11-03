#!/usr/bin/env bash
set -euo pipefail
NS=net-egress
SEL=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.podSelector.matchLabels.app}')
[ "$SEL" = "client" ]
TYPES=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.policyTypes[*]}')
echo "$TYPES" | grep -q Egress
TO=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.egress[0].to[0].podSelector.matchLabels.app}')
[ "$TO" = "api" ]
PORT=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.egress[0].ports[0].port}')
[ "$PORT" = "8080" ]
exit 0
