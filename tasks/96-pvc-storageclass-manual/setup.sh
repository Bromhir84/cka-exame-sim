#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-96 --dry-run=client -o yaml | kubectl apply -f -
