#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-comp73 --dry-run=client -o yaml | kubectl apply -f -
