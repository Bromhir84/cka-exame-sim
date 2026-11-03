#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-hook78 --dry-run=client -o yaml | kubectl apply -f -
