#!/usr/bin/env bash
set -euo pipefail
C=$(kubectl get pv pv-host-95 -o jsonpath='{.spec.capacity.storage}')
[ "$C" = "5Gi" ]
exit 0
