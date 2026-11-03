#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-limits get limitrange mem-limit-range >/dev/null
exit 0
