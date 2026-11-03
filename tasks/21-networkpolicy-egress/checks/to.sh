#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.egress[0].to[0].podSelector.matchLabels.app}")" = "api" ]
[ "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.egress[0].ports[0].port}")" = "8080" ]
