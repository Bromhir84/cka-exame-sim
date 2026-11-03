#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n net-lb87 get svc web-lb -o jsonpath='{.spec.ports[0].port}')
[ "$P" = "80" ]
exit 0
