#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-deploy59 --dry-run=client -o yaml | kubectl apply -f -
