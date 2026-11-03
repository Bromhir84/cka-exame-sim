#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-hostpath --dry-run=client -o yaml | kubectl apply -f -
