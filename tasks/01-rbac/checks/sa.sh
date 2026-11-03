#!/usr/bin/env bash
set -euo pipefail
kubectl -n rbac-lab get sa deployer >/dev/null
