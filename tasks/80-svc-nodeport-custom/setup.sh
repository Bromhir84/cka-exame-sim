#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-np80 --dry-run=client -o yaml | kubectl apply -f -
