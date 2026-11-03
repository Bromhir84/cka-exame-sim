#!/usr/bin/env bash
set -euo pipefail
kubectl get pv hp-pv >/dev/null
SC=$(kubectl get pv hp-pv -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual" ]
PHASE=$(kubectl -n stor-hostpath get pvc hp-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-hostpath wait --for=condition=Ready pod/hp-pod --timeout=120s
exit 0
