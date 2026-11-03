#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-cmvol --dry-run=client -o yaml | kubectl apply -f -
