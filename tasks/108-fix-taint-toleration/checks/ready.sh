#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-taint108 wait --for=condition=Ready pod/critical --timeout=120s
exit 0
