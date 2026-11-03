#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-pv64 --dry-run=client -o yaml | kubectl apply -f -
