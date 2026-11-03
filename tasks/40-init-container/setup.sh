#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-init --dry-run=client -o yaml | kubectl apply -f -
