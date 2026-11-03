#!/usr/bin/env bash
set -euo pipefail
CMD=$(kubectl -n ts-crash101 get deploy worker -o jsonpath='{.spec.template.spec.containers[0].command[*]}')
echo "$CMD" | grep -q sleep
exit 0
