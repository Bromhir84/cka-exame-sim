#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-sub wait --for=condition=Ready pod/sub-pod --timeout=120s
[ "$(kubectl -n stor-sub get pod sub-pod -o jsonpath="{.spec.containers[0].volumeMounts[0].subPath}")" = "cache" ]
[ "$(kubectl -n stor-sub get pod sub-pod -o jsonpath="{.spec.containers[0].volumeMounts[0].mountPath}")" = "/work" ]
