#!/usr/bin/env bash
set -euo pipefail
NS=net-tls86
[ "$(kubectl -n "$NS" get httproute web-route -o jsonpath='{.spec.parentRefs[0].name}')" = "web-gw" ]
[ "$(kubectl -n "$NS" get httproute web-route -o jsonpath='{.spec.parentRefs[0].sectionName}')" = "https" ]
[ "$(kubectl -n "$NS" get httproute web-route -o jsonpath='{.spec.hostnames[0]}')" = "tls.cka.local" ]
[ "$(kubectl -n "$NS" get httproute web-route -o jsonpath='{.spec.rules[0].matches[0].path.type}')" = "PathPrefix" ]
[ "$(kubectl -n "$NS" get httproute web-route -o jsonpath='{.spec.rules[0].matches[0].path.value}')" = "/" ]
[ "$(kubectl -n "$NS" get httproute web-route -o jsonpath='{.spec.rules[0].backendRefs[0].name}')" = "web" ]
[ "$(kubectl -n "$NS" get httproute web-route -o jsonpath='{.spec.rules[0].backendRefs[0].port}')" = "80" ]
