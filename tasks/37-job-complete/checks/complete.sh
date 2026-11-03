#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-job wait --for=condition=Complete job/pi-job --timeout=120s
exit 0
