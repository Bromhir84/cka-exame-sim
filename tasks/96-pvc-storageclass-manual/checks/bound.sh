#!/usr/bin/env bash
set -euo pipefail
# create helpers if missing so grading is about student objects primarily
PHASE=$(kubectl -n stor-96 get pvc claim-96 -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
exit 0
