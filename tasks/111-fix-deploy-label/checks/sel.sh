#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n ts-lab111 get svc web -o jsonpath='{.spec.selector.app}')
[ "$S" = "web" ]
exit 0
