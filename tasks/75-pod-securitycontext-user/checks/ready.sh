#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-sec75 wait --for=condition=Ready pod/secure-pod --timeout=120s
exit 0
