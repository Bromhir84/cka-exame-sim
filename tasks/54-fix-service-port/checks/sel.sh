#!/usr/bin/env bash
set -euo pipefail
SEL=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "api" ]
exit 0
