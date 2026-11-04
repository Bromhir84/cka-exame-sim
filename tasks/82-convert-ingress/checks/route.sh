#!/usr/bin/env bash
set -euo pipefail
NS=net-ing82
[ "$(kubectl -n "$NS" get httproute echo-route -o jsonpath='{.spec.parentRefs[0].name}')" = "echo-gw" ]
[ "$(kubectl -n "$NS" get httproute echo-route -o jsonpath='{.spec.hostnames[0]}')" = "echo.cka.local" ]
[ "$(kubectl -n "$NS" get httproute echo-route -o jsonpath='{.spec.rules[0].matches[0].path.type}')" = "PathPrefix" ]
[ "$(kubectl -n "$NS" get httproute echo-route -o jsonpath='{.spec.rules[0].matches[0].path.value}')" = "/" ]
[ "$(kubectl -n "$NS" get httproute echo-route -o jsonpath='{.spec.rules[0].backendRefs[0].name}')" = "echo" ]
[ "$(kubectl -n "$NS" get httproute echo-route -o jsonpath='{.spec.rules[0].backendRefs[0].port}')" = "80" ]
