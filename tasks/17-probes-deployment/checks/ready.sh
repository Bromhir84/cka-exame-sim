#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-probes rollout status deploy/probed --timeout=120s
