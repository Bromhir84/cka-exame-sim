#!/usr/bin/env bash
set -euo pipefail
VOL=$(kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.volumes[0].name}')
[ "$VOL" = "cache" ]
kubectl -n stor-empty get pod cache-pod -o json | grep -q emptyDir
exit 0
