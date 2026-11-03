#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrolebinding user-impersonator-binding >/dev/null
exit 0
