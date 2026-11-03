#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-cme98 --dry-run=client -o yaml | kubectl apply -f -
