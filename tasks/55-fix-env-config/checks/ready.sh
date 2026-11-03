#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-env rollout status deploy/worker --timeout=120s
exit 0
