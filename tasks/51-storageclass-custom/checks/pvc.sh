#!/usr/bin/env bash
set -euo pipefail
SC=$(kubectl -n stor-sc-custom get pvc fast-pvc -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "fast-local" ]
exit 0
