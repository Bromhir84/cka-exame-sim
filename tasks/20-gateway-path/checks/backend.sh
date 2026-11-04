#!/usr/bin/env bash
set -euo pipefail
NS=net-ingpath
[ "$(kubectl -n "$NS" get httproute shop-route -o jsonpath='{.spec.parentRefs[0].name}')" = "shop-gw" ]
[ "$(kubectl -n "$NS" get httproute shop-route -o jsonpath='{.spec.rules[0].backendRefs[0].name}')" = "shop" ]
[ "$(kubectl -n "$NS" get httproute shop-route -o jsonpath='{.spec.rules[0].backendRefs[0].port}')" = "80" ]
