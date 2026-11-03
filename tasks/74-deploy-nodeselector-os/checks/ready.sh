#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-os74 rollout status deploy/linux-web --timeout=120s
exit 0
