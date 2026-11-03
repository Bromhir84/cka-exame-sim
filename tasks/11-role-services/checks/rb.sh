#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-svc-rbac get rolebinding svc-manager-binding >/dev/null
