#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-os74 --dry-run=client -o yaml | kubectl apply -f -
