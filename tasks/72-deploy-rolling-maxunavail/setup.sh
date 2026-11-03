#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-roll72 --dry-run=client -o yaml | kubectl apply -f -
