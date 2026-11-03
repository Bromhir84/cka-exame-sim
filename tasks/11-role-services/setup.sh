#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-svc-rbac --dry-run=client -o yaml | kubectl apply -f -
