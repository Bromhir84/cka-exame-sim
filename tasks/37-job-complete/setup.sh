#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-job --dry-run=client -o yaml | kubectl apply -f -
