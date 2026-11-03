#!/usr/bin/env bash
set -euo pipefail
H=$(kubectl -n net-ing82 get ingress echo-ing -o jsonpath='{.spec.rules[0].host}')
[ "$H" = "echo.cka.local" ]
exit 0
