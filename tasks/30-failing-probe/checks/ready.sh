#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-probe rollout status deploy/web --timeout=120s
[ "$(kubectl -n ts-probe get deploy web -o jsonpath="{.status.readyReplicas}")" = "2" ]
