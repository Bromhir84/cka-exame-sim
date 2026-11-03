#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n net-svclabel get svc fe-svc -o jsonpath="{.spec.selector.tier}")" = "frontend" ]
[ "$(kubectl -n net-svclabel get svc fe-svc -o jsonpath="{.spec.selector.env}")" = "prod" ]
