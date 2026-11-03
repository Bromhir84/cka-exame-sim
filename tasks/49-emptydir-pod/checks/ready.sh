#!/usr/bin/env bash
set -euo pipefail
MP=$(kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/cache" ]
kubectl -n stor-empty wait --for=condition=Ready pod/cache-pod --timeout=120s
exit 0
