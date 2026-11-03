#!/usr/bin/env bash
set -euo pipefail
CL=$(kubectl -n stor-pvc91 get pod data-pod -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}')
[ "$CL" = "data-pvc" ]
MP=$(kubectl -n stor-pvc91 get pod data-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/data" ]
PHASE=$(kubectl -n stor-pvc91 get pvc data-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-pvc91 wait --for=condition=Ready pod/data-pod --timeout=120s
exit 0
