#!/usr/bin/env bash
set -euo pipefail
# Selector was already correct — only pass once the Service actually has endpoints
# (which requires the targetPort fix).
SEL=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "api" ]
TP=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "8080" ]
EP=$(kubectl -n ts-port get endpoints api-svc -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
