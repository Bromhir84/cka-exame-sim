#!/usr/bin/env bash
set -euo pipefail

NS=storage-lab
SIZE=$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.resources.requests.storage}')
[ "$SIZE" = "1Gi" ]
MODE=$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.accessModes[0]}')
[ "$MODE" = "ReadWriteOnce" ]
SC=$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "standard" ]

PHASE=$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.status.phase}')
# Bound may wait for pod with WaitForFirstConsumer
kubectl -n "$NS" wait --for=condition=Ready pod/data-pod --timeout=120s
PHASE=$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]

MOUNT=$(kubectl -n "$NS" get pod data-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
echo "$MOUNT" | grep -q '/data'
CLAIM=$(kubectl -n "$NS" get pod data-pod -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}')
[ "$CLAIM" = "data-pvc" ]

exit 0
