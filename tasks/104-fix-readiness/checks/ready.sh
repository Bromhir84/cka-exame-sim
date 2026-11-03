#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-ready104 rollout status deploy/api --timeout=120s
exit 0
