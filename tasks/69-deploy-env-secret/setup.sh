#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-env69 --dry-run=client -o yaml | kubectl apply -f -
