#!/usr/bin/env bash
set -euo pipefail
NP=$(kubectl -n net-np80 get svc web-np -o jsonpath='{.spec.ports[0].nodePort}')
[ "$NP" = "30080" ]
exit 0
