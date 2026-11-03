#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-envfrom76 --dry-run=client -o yaml | kubectl apply -f -
