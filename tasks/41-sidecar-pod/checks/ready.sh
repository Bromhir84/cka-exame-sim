#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-sidecar wait --for=condition=Ready pod/pair --timeout=120s
exit 0
