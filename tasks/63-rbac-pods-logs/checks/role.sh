#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl -n arch-logs63 get role log-reader -o jsonpath='{.rules[*].resources[*]}')
echo "$RES" | grep -q pods
echo "$RES" | grep -q pods/log
exit 0
