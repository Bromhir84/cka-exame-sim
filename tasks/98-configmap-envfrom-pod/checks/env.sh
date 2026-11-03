#!/usr/bin/env bash
set -euo pipefail
N=$(kubectl -n stor-cme98 get pod cfg-pod -o jsonpath='{.spec.containers[0].envFrom[0].configMapRef.name}')
[ "$N" = "cfg" ]
exit 0
