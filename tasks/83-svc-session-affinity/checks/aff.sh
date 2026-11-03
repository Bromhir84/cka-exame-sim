#!/usr/bin/env bash
set -euo pipefail
A=$(kubectl -n net-aff83 get svc sticky -o jsonpath='{.spec.sessionAffinity}')
[ "$A" = "ClientIP" ]
exit 0
