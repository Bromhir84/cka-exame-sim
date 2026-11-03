#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-mem97 wait --for=condition=Ready pod/mem-pod --timeout=120s
exit 0
