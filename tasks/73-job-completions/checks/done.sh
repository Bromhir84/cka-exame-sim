#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-comp73 wait --for=condition=Complete job/batch --timeout=180s
exit 0
