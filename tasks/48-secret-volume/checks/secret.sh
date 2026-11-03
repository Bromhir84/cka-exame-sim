#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-secvol get secret app-tls >/dev/null
exit 0
