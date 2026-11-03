#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-cme98 wait --for=condition=Ready pod/cfg-pod --timeout=120s
exit 0
