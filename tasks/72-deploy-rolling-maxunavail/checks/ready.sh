#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-roll72 rollout status deploy/api --timeout=180s
exit 0
