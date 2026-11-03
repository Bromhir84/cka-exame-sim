#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n stor-ro99 get pvc ro-claim -o jsonpath='{.status.phase}')
[ "$P" = "Bound" ]
exit 0
