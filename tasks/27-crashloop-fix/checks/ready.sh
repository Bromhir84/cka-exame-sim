#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-crash rollout status deploy/looper --timeout=120s
[ "$(kubectl -n ts-crash get deploy looper -o jsonpath="{.status.readyReplicas}")" = "1" ]
