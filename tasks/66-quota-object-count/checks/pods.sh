#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n arch-count66 get resourcequota object-counts -o jsonpath='{.spec.hard.pods}')
[ "$P" = "10" ]
exit 0
