#!/usr/bin/env bash
set -euo pipefail
CPU=$(kubectl -n arch-quota61 get resourcequota compute-quota -o jsonpath='{.spec.hard.requests\.cpu}')
[ "$CPU" = "1" ]
MEM=$(kubectl -n arch-quota61 get resourcequota compute-quota -o jsonpath='{.spec.hard.requests\.memory}')
echo "$MEM" | grep -Eq '1Gi|1024Mi'
LCPU=$(kubectl -n arch-quota61 get resourcequota compute-quota -o jsonpath='{.spec.hard.limits\.cpu}')
[ "$LCPU" = "2" ]
exit 0
