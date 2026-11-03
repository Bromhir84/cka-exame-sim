#!/usr/bin/env bash
set -euo pipefail
# Port/selector were already correct — require working endpoints after the fix.
[ "$(kubectl -n ts-target get svc echo-svc -o jsonpath="{.spec.ports[0].port}")" = "80" ]
[ "$(kubectl -n ts-target get svc echo-svc -o jsonpath="{.spec.selector.app}")" = "echo" ]
TP=$(kubectl -n ts-target get svc echo-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "8080" ]
EP=$(kubectl -n ts-target get endpoints echo-svc -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
