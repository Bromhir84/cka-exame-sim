#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl get clusterrole pv-viewer -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q persistentvolumes
exit 0
