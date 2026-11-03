#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-limits rollout status deploy/limited --timeout=120s
