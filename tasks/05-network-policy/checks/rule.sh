#!/usr/bin/env bash
set -euo pipefail

NS=policy-lab
[ "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.ingress[0].from[0].podSelector.matchLabels.role}')" = "frontend" ]
[ "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.ingress[0].ports[0].port}')" = "5432" ]
