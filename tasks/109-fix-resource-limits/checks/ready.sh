#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-res109 wait --for=condition=Ready pod/heavy --timeout=120s
exit 0
