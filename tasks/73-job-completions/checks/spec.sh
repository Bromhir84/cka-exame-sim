#!/usr/bin/env bash
set -euo pipefail
C=$(kubectl -n wl-comp73 get job batch -o jsonpath='{.spec.completions}')
[ "$C" = "3" ]
P=$(kubectl -n wl-comp73 get job batch -o jsonpath='{.spec.parallelism}')
[ "$P" = "1" ]
exit 0
