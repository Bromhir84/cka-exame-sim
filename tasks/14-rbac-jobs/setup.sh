#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-jobs --dry-run=client -o yaml | kubectl apply -f -
