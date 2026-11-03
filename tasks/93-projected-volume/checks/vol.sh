#!/usr/bin/env bash
set -euo pipefail
JSON=$(kubectl -n stor-proj93 get pod proj-pod -o json)
echo "$JSON" | grep -q '"projected"'
echo "$JSON" | grep -q p-cm
echo "$JSON" | grep -q p-sec
exit 0
