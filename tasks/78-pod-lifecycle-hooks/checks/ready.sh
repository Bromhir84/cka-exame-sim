#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-hook78 wait --for=condition=Ready pod/hook-pod --timeout=120s
exit 0
