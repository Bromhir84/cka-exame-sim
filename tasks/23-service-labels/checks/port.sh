#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n net-svclabel get svc fe-svc -o jsonpath="{.spec.ports[0].port}")" = "80" ]
