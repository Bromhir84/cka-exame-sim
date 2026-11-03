#!/usr/bin/env bash
set -euo pipefail
MU=$(kubectl -n wl-roll72 get deploy api -o jsonpath='{.spec.strategy.rollingUpdate.maxUnavailable}')
[ "$MU" = "0" ]
MS=$(kubectl -n wl-roll72 get deploy api -o jsonpath='{.spec.strategy.rollingUpdate.maxSurge}')
[ "$MS" = "1" ]
exit 0
