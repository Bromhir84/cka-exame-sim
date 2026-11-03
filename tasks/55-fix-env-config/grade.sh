#!/usr/bin/env bash
set -euo pipefail
VAL=$(kubectl -n ts-env get cm worker-config -o jsonpath='{.data.MODE}')
[ "$VAL" = "batch" ]
kubectl -n ts-env rollout status deploy/worker --timeout=120s
exit 0
