#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace rbac-lab --dry-run=client -o yaml | kubectl apply -f -
