#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n stor-sc get pvc app-data -o jsonpath="{.spec.resources.requests.storage}")" = "2Gi" ]
[ "$(kubectl -n stor-sc get pvc app-data -o jsonpath="{.spec.storageClassName}")" = "standard" ]
