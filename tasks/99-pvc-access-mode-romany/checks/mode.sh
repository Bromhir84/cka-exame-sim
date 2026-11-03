#!/usr/bin/env bash
set -euo pipefail
M=$(kubectl -n stor-ro99 get pvc ro-claim -o jsonpath='{.spec.accessModes[0]}')
[ "$M" = "ReadOnlyMany" ]
exit 0
