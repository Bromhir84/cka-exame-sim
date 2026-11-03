#!/usr/bin/env bash
set -euo pipefail
CPU=$(kubectl -n ts-res109 get pod heavy -o jsonpath='{.spec.containers[0].resources.requests.cpu}')
[ "$CPU" = "100m" ]
exit 0
