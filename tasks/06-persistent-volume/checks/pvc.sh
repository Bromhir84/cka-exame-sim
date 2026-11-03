#!/usr/bin/env bash
set -euo pipefail

NS=storage-lab
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.resources.requests.storage}')" = "1Gi" ]
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.accessModes[0]}')" = "ReadWriteOnce" ]
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.storageClassName}')" = "standard" ]
