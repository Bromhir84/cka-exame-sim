#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-envfrom76 get cm app-config >/dev/null
exit 0
