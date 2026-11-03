#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-mem97 --dry-run=client -o yaml | kubectl apply -f -
