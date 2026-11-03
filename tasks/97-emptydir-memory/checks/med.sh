#!/usr/bin/env bash
set -euo pipefail
M=$(kubectl -n stor-mem97 get pod mem-pod -o jsonpath='{.spec.volumes[0].emptyDir.medium}')
[ "$M" = "Memory" ]
exit 0
