#!/usr/bin/env bash
set -euo pipefail
VAL=$(kubectl -n stor-cmvol get cm app-files -o jsonpath='{.data.config\.txt}')
[ "$VAL" = "hello-cka" ]
MP=$(kubectl -n stor-cmvol get pod cm-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/etc/config" ]
kubectl -n stor-cmvol wait --for=condition=Ready pod/cm-pod --timeout=120s
exit 0
