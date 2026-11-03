#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-svc-rbac get sa svc-manager >/dev/null
