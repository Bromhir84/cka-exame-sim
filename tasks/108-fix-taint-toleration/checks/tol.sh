#!/usr/bin/env bash
set -euo pipefail
K=$(kubectl -n ts-taint108 get pod critical -o jsonpath='{.spec.tolerations[0].key}')
[ "$K" = "dedicated" ]
E=$(kubectl -n ts-taint108 get pod critical -o jsonpath='{.spec.tolerations[0].effect}')
[ "$E" = "NoSchedule" ]
exit 0
