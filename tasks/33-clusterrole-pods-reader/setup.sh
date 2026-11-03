#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-pods --dry-run=client -o yaml | kubectl apply -f -
