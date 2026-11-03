#!/usr/bin/env bash
set -euo pipefail
E=$(kubectl -n net-eg84 get networkpolicy deny-egress -o jsonpath='{.spec.egress[*]}')
[ -z "$E" ]
exit 0
