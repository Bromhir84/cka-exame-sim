#!/usr/bin/env bash
set -euo pipefail

kubectl -n broken-app rollout status deploy/frontend --timeout=120s
[ "$(kubectl -n broken-app get deploy frontend -o jsonpath='{.status.readyReplicas}')" = "2" ]
