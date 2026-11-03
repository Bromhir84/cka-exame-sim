#!/usr/bin/env bash
set -euo pipefail
IP=$(kubectl -n net-ep85 get endpoints external-web -o jsonpath='{.subsets[0].addresses[0].ip}')
[ "$IP" = "1.2.3.4" ]
exit 0
