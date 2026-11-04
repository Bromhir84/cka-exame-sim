#!/usr/bin/env bash
set -euo pipefail
NS=net-twohost
[ "$(kubectl -n "$NS" get httproute beta -o jsonpath='{.spec.parentRefs[0].name}')" = "web-gw" ]
[ "$(kubectl -n "$NS" get httproute beta -o jsonpath='{.spec.hostnames[0]}')" = "beta.cka.local" ]
[ "$(kubectl -n "$NS" get httproute beta -o jsonpath='{.spec.rules[0].backendRefs[0].name}')" = "beta-svc" ]
[ "$(kubectl -n "$NS" get httproute beta -o jsonpath='{.spec.rules[0].backendRefs[0].port}')" = "80" ]
