#!/usr/bin/env bash
set -euo pipefail
REQ=$(kubectl -n arch-limits get limitrange mem-limit-range -o jsonpath='{.spec.limits[0].defaultRequest.memory}')
[ "$REQ" = "64Mi" ]
LIM=$(kubectl -n arch-limits get limitrange mem-limit-range -o jsonpath='{.spec.limits[0].default.memory}')
[ "$LIM" = "256Mi" ]
exit 0
