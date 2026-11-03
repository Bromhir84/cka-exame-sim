#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-sec105 get secret app-secret >/dev/null
exit 0
