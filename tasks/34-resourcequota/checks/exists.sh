#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-quota get resourcequota team-quota >/dev/null
exit 0
