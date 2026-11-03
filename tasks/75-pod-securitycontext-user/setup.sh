#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-sec75 --dry-run=client -o yaml | kubectl apply -f -
