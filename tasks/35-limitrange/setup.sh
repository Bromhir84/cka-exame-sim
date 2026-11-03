#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-limits --dry-run=client -o yaml | kubectl apply -f -
