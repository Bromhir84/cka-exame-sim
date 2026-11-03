#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl -n arch-events60 get role event-watcher-role -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q events
exit 0
