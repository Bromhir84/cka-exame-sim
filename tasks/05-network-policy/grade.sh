#!/usr/bin/env bash
set -euo pipefail

NS=policy-lab
NP=$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o json)

echo "$NP" | grep -q '"app":"secure-db"\|"app": "secure-db"'
# Also accept jsonpath form
SEL=$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.podSelector.matchLabels.app}')
[ "$SEL" = "secure-db" ]

TYPES=$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.policyTypes[*]}')
echo "$TYPES" | grep -q Ingress

FROM=$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.ingress[0].from[0].podSelector.matchLabels.role}')
[ "$FROM" = "frontend" ]

PORT=$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.ingress[0].ports[0].port}')
PROTO=$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.ingress[0].ports[0].protocol}')
[ "$PORT" = "5432" ]
[ "$PROTO" = "TCP" ] || [ -z "$PROTO" ]

exit 0
