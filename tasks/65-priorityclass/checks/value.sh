#!/usr/bin/env bash
set -euo pipefail
VAL=$(kubectl get priorityclass high-priority-65 -o jsonpath='{.value}')
[ "$VAL" = "1000000" ]
GD=$(kubectl get priorityclass high-priority-65 -o jsonpath='{.globalDefault}')
[ "$GD" = "false" ]
exit 0
