#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-env69 get secret app-secret >/dev/null
exit 0
