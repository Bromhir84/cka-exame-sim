#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-sc wait --for=condition=Ready pod/app-data-pod --timeout=120s
[ "$(kubectl -n stor-sc get pvc app-data -o jsonpath="{.status.phase}")" = "Bound" ]
[ "$(kubectl -n stor-sc get pod app-data-pod -o jsonpath="{.spec.containers[0].volumeMounts[0].mountPath}")" = "/var/app" ]
