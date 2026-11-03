#!/usr/bin/env bash
set -euo pipefail
MP=$(kubectl -n stor-cmvol get pod cm-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/etc/config" ]
SRC=$(kubectl -n stor-cmvol get pod cm-pod -o jsonpath='{.spec.volumes[0].configMap.name}')
[ "$SRC" = "app-files" ]
kubectl -n stor-cmvol wait --for=condition=Ready pod/cm-pod --timeout=120s
exit 0
