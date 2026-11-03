#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n arch-count66 get resourcequota object-counts -o jsonpath='{.spec.hard.services}')
[ "$S" = "5" ]
exit 0
