#!/usr/bin/env bash
set -euo pipefail
NS=net-lab
[ "$(kubectl -n "$NS" get httproute hello-route -o jsonpath='{.spec.parentRefs[0].name}')" = "hello-gw" ]
[ "$(kubectl -n "$NS" get httproute hello-route -o jsonpath='{.spec.hostnames[0]}')" = "hello.cka.local" ]
[ "$(kubectl -n "$NS" get httproute hello-route -o jsonpath='{.spec.rules[0].matches[0].path.type}')" = "PathPrefix" ]
[ "$(kubectl -n "$NS" get httproute hello-route -o jsonpath='{.spec.rules[0].matches[0].path.value}')" = "/" ]
[ "$(kubectl -n "$NS" get httproute hello-route -o jsonpath='{.spec.rules[0].backendRefs[0].name}')" = "hello-svc" ]
[ "$(kubectl -n "$NS" get httproute hello-route -o jsonpath='{.spec.rules[0].backendRefs[0].port}')" = "80" ]
