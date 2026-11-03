#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-rep107 rollout status deploy/web --timeout=120s
exit 0
