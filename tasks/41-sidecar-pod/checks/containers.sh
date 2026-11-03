#!/usr/bin/env bash
set -euo pipefail
NAMES=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[*].name}')
echo "$NAMES" | grep -qw app
echo "$NAMES" | grep -qw sidecar
exit 0
