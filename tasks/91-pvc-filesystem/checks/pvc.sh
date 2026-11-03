#!/usr/bin/env bash
set -euo pipefail
SZ=$(kubectl -n stor-pvc91 get pvc data-pvc -o jsonpath='{.spec.resources.requests.storage}')
[ "$SZ" = "2Gi" ]
MODE=$(kubectl -n stor-pvc91 get pvc data-pvc -o jsonpath='{.spec.accessModes[0]}')
[ "$MODE" = "ReadWriteOnce" ]
exit 0
