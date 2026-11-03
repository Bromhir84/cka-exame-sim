#!/usr/bin/env bash
set -euo pipefail
PHASE=$(kubectl -n stor-hostpath get pvc hp-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-hostpath wait --for=condition=Ready pod/hp-pod --timeout=120s
exit 0
