#!/usr/bin/env bash
set -euo pipefail
CIP=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.clusterIP}')
[ "$CIP" = "None" ]
exit 0
