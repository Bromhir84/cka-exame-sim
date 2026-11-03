#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.selector.app}")" = "web" ]
