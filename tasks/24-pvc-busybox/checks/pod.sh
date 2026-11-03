#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-busy wait --for=condition=Ready pod/busy-pod --timeout=120s
[ "$(kubectl -n stor-busy get pvc busy-pvc -o jsonpath="{.status.phase}")" = "Bound" ]
[ "$(kubectl -n stor-busy get pod busy-pod -o jsonpath="{.spec.volumes[0].persistentVolumeClaim.claimName}")" = "busy-pvc" ]
