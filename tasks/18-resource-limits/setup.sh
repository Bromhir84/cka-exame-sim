#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-limits --dry-run=client -o yaml | kubectl apply -f -
