#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-logs63 get rolebinding log-reader-binding >/dev/null
exit 0
