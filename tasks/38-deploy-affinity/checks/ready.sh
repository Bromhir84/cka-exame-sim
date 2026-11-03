#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-affinity rollout status deploy/placed --timeout=120s
exit 0
