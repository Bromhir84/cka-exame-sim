#!/usr/bin/env bash
set -euo pipefail
TP=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "8080" ]
SEL=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "api" ]
exit 0
