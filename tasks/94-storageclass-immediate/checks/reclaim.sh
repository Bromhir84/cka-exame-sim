#!/usr/bin/env bash
set -euo pipefail
R=$(kubectl get sc fast-immediate -o jsonpath='{.reclaimPolicy}')
[ "$R" = "Delete" ]
exit 0
