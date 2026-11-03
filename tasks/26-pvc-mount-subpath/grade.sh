#!/usr/bin/env bash
set -euo pipefail
NS=stor-sub
kubectl -n "$NS" wait --for=condition=Ready pod/sub-pod --timeout=120s
SP=$(kubectl -n "$NS" get pod sub-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].subPath}')
[ "$SP" = "cache" ]
MP=$(kubectl -n "$NS" get pod sub-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/work" ]
PHASE=$(kubectl -n "$NS" get pvc sub-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
exit 0
