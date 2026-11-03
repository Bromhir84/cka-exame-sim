#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n stor-sub get pvc sub-pvc -o jsonpath="{.status.phase}")" = "Bound" ]
