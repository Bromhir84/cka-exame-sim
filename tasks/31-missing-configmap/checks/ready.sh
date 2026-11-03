#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-cm rollout status deploy/cfg-app --timeout=120s
[ "$(kubectl -n ts-cm get deploy cfg-app -o jsonpath="{.status.readyReplicas}")" = "1" ]
