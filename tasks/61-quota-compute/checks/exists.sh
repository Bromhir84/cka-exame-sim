#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-quota61 get resourcequota compute-quota >/dev/null
exit 0
