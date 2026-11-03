#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-lr62 get limitrange pod-limits >/dev/null
exit 0
