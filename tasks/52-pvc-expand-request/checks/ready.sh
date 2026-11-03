#!/usr/bin/env bash
set -euo pipefail
PHASE=$(kubectl -n stor-big get pvc big-data -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-big wait --for=condition=Ready pod/big-pod --timeout=180s
exit 0
