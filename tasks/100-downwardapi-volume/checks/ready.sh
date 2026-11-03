#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-down100 wait --for=condition=Ready pod/down-pod --timeout=120s
exit 0
