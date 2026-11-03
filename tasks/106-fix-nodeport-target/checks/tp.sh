#!/usr/bin/env bash
set -euo pipefail
TP=$(kubectl -n ts-port106 get svc web -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "80" ]
exit 0
