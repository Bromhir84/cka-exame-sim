#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-proj93 --dry-run=client -o yaml | kubectl apply -f -
