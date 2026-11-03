#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-eg84 --dry-run=client -o yaml | kubectl apply -f -
