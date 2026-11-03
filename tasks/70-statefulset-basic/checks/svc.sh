#!/usr/bin/env bash
set -euo pipefail
CIP=$(kubectl -n wl-sts70 get svc web -o jsonpath='{.spec.clusterIP}')
[ "$CIP" = "None" ]
exit 0
