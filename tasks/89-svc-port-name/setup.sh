#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-name89 --dry-run=client -o yaml | kubectl apply -f -
