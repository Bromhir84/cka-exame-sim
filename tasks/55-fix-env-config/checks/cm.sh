#!/usr/bin/env bash
set -euo pipefail
VAL=$(kubectl -n ts-env get cm worker-config -o jsonpath='{.data.MODE}')
[ "$VAL" = "batch" ]
exit 0
