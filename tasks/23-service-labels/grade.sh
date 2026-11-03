#!/usr/bin/env bash
set -euo pipefail
NS=net-svclabel
T=$(kubectl -n "$NS" get svc fe-svc -o jsonpath='{.spec.selector.tier}')
E=$(kubectl -n "$NS" get svc fe-svc -o jsonpath='{.spec.selector.env}')
[ "$T" = "frontend" ]
[ "$E" = "prod" ]
P=$(kubectl -n "$NS" get svc fe-svc -o jsonpath='{.spec.ports[0].port}')
[ "$P" = "80" ]
exit 0
