#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-ro99 --dry-run=client -o yaml | kubectl apply -f -
