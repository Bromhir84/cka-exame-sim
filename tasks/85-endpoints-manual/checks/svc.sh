#!/usr/bin/env bash
set -euo pipefail
kubectl -n net-ep85 get svc external-web >/dev/null
SEL=$(kubectl -n net-ep85 get svc external-web -o jsonpath='{.spec.selector}')
[ -z "$SEL" ]
exit 0
