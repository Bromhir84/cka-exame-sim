#!/usr/bin/env bash
set -euo pipefail
NS=net-multiport
TYPE=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.type}')
[ "$TYPE" = "ClusterIP" ] || [ -z "$TYPE" ]
N0=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[0].name}')
N1=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[1].name}')
echo "$N0$N1" | grep -q http
echo "$N0$N1" | grep -q metrics
PORTS=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[*].port}')
echo "$PORTS" | grep -q 80
echo "$PORTS" | grep -q 8080
exit 0
