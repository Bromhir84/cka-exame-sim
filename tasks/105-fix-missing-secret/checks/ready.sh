#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-sec105 wait --for=condition=Ready pod/need-secret --timeout=120s
exit 0
