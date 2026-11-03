#!/usr/bin/env bash
set -euo pipefail
T=$(kubectl -n net-lb87 get svc web-lb -o jsonpath='{.spec.type}')
[ "$T" = "LoadBalancer" ]
exit 0
