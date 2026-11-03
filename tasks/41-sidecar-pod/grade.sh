#!/usr/bin/env bash
set -euo pipefail
C1=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[0].name}')
C2=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[1].name}')
echo "$C1 $C2" | grep -q app
echo "$C1 $C2" | grep -q sidecar
COUNT=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[*].name}' | wc -w)
[ "$COUNT" -eq 2 ]
kubectl -n wl-sidecar wait --for=condition=Ready pod/pair --timeout=120s
exit 0
