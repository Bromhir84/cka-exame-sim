#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-crash101 rollout status deploy/worker --timeout=120s
exit 0
