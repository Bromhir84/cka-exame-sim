#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-cm110 wait --for=condition=Ready pod/need-cm --timeout=120s
exit 0
