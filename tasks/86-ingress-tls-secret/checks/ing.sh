#!/usr/bin/env bash
set -euo pipefail
SN=$(kubectl -n net-tls86 get ingress web-tls-ing -o jsonpath='{.spec.tls[0].secretName}')
[ "$SN" = "web-tls" ]
H=$(kubectl -n net-tls86 get ingress web-tls-ing -o jsonpath='{.spec.rules[0].host}')
[ "$H" = "tls.cka.local" ]
exit 0
