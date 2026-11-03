#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-empty --dry-run=client -o yaml | kubectl apply -f -
