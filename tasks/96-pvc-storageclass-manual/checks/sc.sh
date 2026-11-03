#!/usr/bin/env bash
set -euo pipefail
SC=$(kubectl -n stor-96 get pvc claim-96 -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual-96" ]
exit 0
