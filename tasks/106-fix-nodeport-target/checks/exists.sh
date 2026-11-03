#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-port106 get svc web >/dev/null
exit 0
