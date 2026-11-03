#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n stor-busy get pvc busy-pvc -o jsonpath="{.spec.resources.requests.storage}")" = "500Mi" ]
[ "$(kubectl -n stor-busy get pvc busy-pvc -o jsonpath="{.spec.storageClassName}")" = "standard" ]
