#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-sec92 --dry-run=client -o yaml | kubectl apply -f -
