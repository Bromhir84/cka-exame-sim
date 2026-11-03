#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n ts-svc103 get svc web -o jsonpath='{.spec.selector.app}')
[ "$S" = "web" ]
exit 0
