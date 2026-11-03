#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-quota get resourcequota team-quota >/dev/null
CPU=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.requests\.cpu}')
[ "$CPU" = "2" ]
MEM=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.requests\.memory}')
[ "$MEM" = "2Gi" ]
PODS=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.pods}')
[ "$PODS" = "10" ]
exit 0
