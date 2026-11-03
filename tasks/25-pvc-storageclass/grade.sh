#!/usr/bin/env bash
set -euo pipefail
NS=stor-sc
SIZE=$(kubectl -n "$NS" get pvc app-data -o jsonpath='{.spec.resources.requests.storage}')
[ "$SIZE" = "2Gi" ]
SC=$(kubectl -n "$NS" get pvc app-data -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "standard" ]
kubectl -n "$NS" wait --for=condition=Ready pod/app-data-pod --timeout=120s
PHASE=$(kubectl -n "$NS" get pvc app-data -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
MP=$(kubectl -n "$NS" get pod app-data-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/var/app" ]
exit 0
