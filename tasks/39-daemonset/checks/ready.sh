#!/usr/bin/env bash
set -euo pipefail
# wait a bit for scheduling
for i in 1 2 3 4 5 6 7 8 9 10; do
  DESIRED=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.status.desiredNumberScheduled}')
  READY=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.status.numberReady}')
  if [ -n "$DESIRED" ] && [ "$DESIRED" != "0" ] && [ "$READY" = "$DESIRED" ]; then
    exit 0
  fi
  sleep 3
done
exit 1
exit 0
