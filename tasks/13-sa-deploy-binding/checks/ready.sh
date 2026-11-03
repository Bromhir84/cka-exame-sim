#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-sa-deploy rollout status deploy/sa-demo --timeout=120s
