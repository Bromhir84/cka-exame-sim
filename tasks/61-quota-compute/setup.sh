#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-quota61 --dry-run=client -o yaml | kubectl apply -f -
