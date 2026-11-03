#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-sts70 --dry-run=client -o yaml | kubectl apply -f -
