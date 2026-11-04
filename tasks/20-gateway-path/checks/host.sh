#!/usr/bin/env bash
set -euo pipefail
NS=net-ingpath
[ "$(kubectl -n "$NS" get httproute shop-route -o jsonpath='{.spec.hostnames[0]}')" = "shop.cka.local" ]
[ "$(kubectl -n "$NS" get httproute shop-route -o jsonpath='{.spec.rules[0].matches[0].path.type}')" = "PathPrefix" ]
[ "$(kubectl -n "$NS" get httproute shop-route -o jsonpath='{.spec.rules[0].matches[0].path.value}')" = "/shop" ]
