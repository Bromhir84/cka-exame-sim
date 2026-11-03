#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-count66 --dry-run=client -o yaml | kubectl apply -f -
