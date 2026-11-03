#!/usr/bin/env bash
set -euo pipefail
EP=$(kubectl -n ts-lab111 get endpoints web -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
kubectl -n ts-lab111 rollout status deploy/web --timeout=60s
exit 0
