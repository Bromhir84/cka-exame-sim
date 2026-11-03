#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-sa-deploy --dry-run=client -o yaml | kubectl apply -f -
