#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-proj93 wait --for=condition=Ready pod/proj-pod --timeout=120s
exit 0
