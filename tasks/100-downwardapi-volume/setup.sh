#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-down100 --dry-run=client -o yaml | kubectl apply -f -
