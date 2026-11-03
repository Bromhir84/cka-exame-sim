#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-crb --dry-run=client -o yaml | kubectl apply -f -
