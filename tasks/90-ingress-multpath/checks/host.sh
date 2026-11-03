#!/usr/bin/env bash
set -euo pipefail
H=$(kubectl -n net-mp90 get ingress split -o jsonpath='{.spec.rules[0].host}')
[ "$H" = "split.cka.local" ]
exit 0
