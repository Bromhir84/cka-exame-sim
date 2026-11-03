#!/usr/bin/env bash
set -euo pipefail
for i in $(seq 1 30); do
  RR=$(kubectl -n wl-rs77 get rs web -o jsonpath='{.status.readyReplicas}')
  [ "${RR:-0}" = "4" ] && exit 0
  sleep 2
done
exit 1
