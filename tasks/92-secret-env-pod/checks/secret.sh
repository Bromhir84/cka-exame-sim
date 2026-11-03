#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-sec92 get secret db-creds >/dev/null
exit 0
