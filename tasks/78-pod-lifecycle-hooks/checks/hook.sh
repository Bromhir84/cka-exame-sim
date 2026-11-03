#!/usr/bin/env bash
set -euo pipefail
CMD=$(kubectl -n wl-hook78 get pod hook-pod -o jsonpath='{.spec.containers[0].lifecycle.postStart.exec.command[*]}')
echo "$CMD" | grep -q hooked
exit 0
