#!/usr/bin/env bash
set -euo pipefail
VAL=$(kubectl -n stor-cmvol get cm app-files -o jsonpath='{.data.config\.txt}')
[ "$VAL" = "hello-cka" ]
exit 0
