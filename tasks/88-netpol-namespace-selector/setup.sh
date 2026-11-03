#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-ns88 --dry-run=client -o yaml | kubectl apply -f -
