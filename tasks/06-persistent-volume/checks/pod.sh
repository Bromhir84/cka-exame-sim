#!/usr/bin/env bash
set -euo pipefail

NS=storage-lab
kubectl -n "$NS" wait --for=condition=Ready pod/data-pod --timeout=120s
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.status.phase}')" = "Bound" ]
echo "$(kubectl -n "$NS" get pod data-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')" | grep -q '/data'
[ "$(kubectl -n "$NS" get pod data-pod -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}')" = "data-pvc" ]
