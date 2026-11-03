#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n net-tls86 get secret web-tls -o jsonpath='{.type}')
[ "$TYPE" = "kubernetes.io/tls" ]
exit 0
