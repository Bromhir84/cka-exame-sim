#!/usr/bin/env bash
set -euo pipefail
if kubectl -n net-ing82 get ingress echo-ing >/dev/null 2>&1; then
  echo "Ingress echo-ing still exists"
  exit 1
fi
