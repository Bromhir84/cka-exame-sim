#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-img102 rollout status deploy/site --timeout=120s
exit 0
