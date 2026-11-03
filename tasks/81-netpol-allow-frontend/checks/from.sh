#!/usr/bin/env bash
set -euo pipefail
FROM=$(kubectl -n net-np81 get networkpolicy allow-frontend -o jsonpath='{.spec.ingress[0].from[0].podSelector.matchLabels.app}')
[ "$FROM" = "frontend" ]
PORT=$(kubectl -n net-np81 get networkpolicy allow-frontend -o jsonpath='{.spec.ingress[0].ports[0].port}')
[ "$PORT" = "80" ]
exit 0
