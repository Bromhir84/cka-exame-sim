#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-cron71 --dry-run=client -o yaml | kubectl apply -f -
