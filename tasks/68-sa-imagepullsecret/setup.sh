#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-pull68 --dry-run=client -o yaml | kubectl apply -f -
