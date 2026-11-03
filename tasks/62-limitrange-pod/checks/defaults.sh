#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n arch-lr62 get limitrange pod-limits -o jsonpath='{.spec.limits[0].type}')
[ "$TYPE" = "Container" ]
DR=$(kubectl -n arch-lr62 get limitrange pod-limits -o jsonpath='{.spec.limits[0].defaultRequest.cpu}')
[ "$DR" = "100m" ]
DL=$(kubectl -n arch-lr62 get limitrange pod-limits -o jsonpath='{.spec.limits[0].default.cpu}')
[ "$DL" = "500m" ]
exit 0
