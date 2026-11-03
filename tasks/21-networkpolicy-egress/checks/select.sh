#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.podSelector.matchLabels.app}")" = "client" ]
echo "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.policyTypes[*]}")" | grep -q Egress
