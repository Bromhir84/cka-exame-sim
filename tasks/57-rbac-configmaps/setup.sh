#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-cm57 --dry-run=client -o yaml | kubectl apply -f -
