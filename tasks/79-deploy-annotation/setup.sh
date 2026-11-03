#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-ann79 --dry-run=client -o yaml | kubectl apply -f -
