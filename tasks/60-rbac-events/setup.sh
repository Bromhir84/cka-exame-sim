#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-events60 --dry-run=client -o yaml | kubectl apply -f -
