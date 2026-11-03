#!/usr/bin/env bash
set -euo pipefail
NS=stor-busy
SIZE=$(kubectl -n "$NS" get pvc busy-pvc -o jsonpath='{.spec.resources.requests.storage}')
[ "$SIZE" = "500Mi" ]
SC=$(kubectl -n "$NS" get pvc busy-pvc -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "standard" ]
kubectl -n "$NS" wait --for=condition=Ready pod/busy-pod --timeout=120s
PHASE=$(kubectl -n "$NS" get pvc busy-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
CLAIM=$(kubectl -n "$NS" get pod busy-pod -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}')
[ "$CLAIM" = "busy-pvc" ]
exit 0
