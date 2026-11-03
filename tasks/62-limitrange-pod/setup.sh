#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-lr62 --dry-run=client -o yaml | kubectl apply -f -
