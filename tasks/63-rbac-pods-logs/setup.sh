#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-logs63 --dry-run=client -o yaml | kubectl apply -f -
