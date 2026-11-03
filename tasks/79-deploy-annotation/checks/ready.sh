#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-ann79 rollout status deploy/annotated --timeout=120s
exit 0
