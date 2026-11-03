#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-nodes58 --dry-run=client -o yaml | kubectl apply -f -
