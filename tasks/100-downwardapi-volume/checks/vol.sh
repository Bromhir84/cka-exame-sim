#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n stor-down100 get pod down-pod -o jsonpath='{.spec.volumes[0].downwardAPI.items[0].path}')
[ "$P" = "pod_name" ]
FP=$(kubectl -n stor-down100 get pod down-pod -o jsonpath='{.spec.volumes[0].downwardAPI.items[0].fieldRef.fieldPath}')
[ "$FP" = "metadata.name" ]
exit 0
