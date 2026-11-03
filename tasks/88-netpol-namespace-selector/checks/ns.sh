#!/usr/bin/env bash
set -euo pipefail
E=$(kubectl -n net-ns88 get networkpolicy allow-from-prod -o jsonpath='{.spec.ingress[0].from[0].namespaceSelector.matchLabels.env}')
[ "$E" = "prod" ]
exit 0
