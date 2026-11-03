#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-probes --dry-run=client -o yaml | kubectl apply -f -
