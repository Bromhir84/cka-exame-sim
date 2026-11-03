#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n net-aff83 get svc sticky -o jsonpath='{.spec.selector.app}')
[ "$S" = "web" ]
exit 0
