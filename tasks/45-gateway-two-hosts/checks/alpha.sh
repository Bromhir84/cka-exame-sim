#!/usr/bin/env bash
set -euo pipefail
NS=net-twohost
[ "$(kubectl -n "$NS" get httproute alpha -o jsonpath='{.spec.parentRefs[0].name}')" = "web-gw" ]
[ "$(kubectl -n "$NS" get httproute alpha -o jsonpath='{.spec.hostnames[0]}')" = "alpha.cka.local" ]
[ "$(kubectl -n "$NS" get httproute alpha -o jsonpath='{.spec.rules[0].backendRefs[0].name}')" = "alpha-svc" ]
[ "$(kubectl -n "$NS" get httproute alpha -o jsonpath='{.spec.rules[0].backendRefs[0].port}')" = "80" ]
