#!/usr/bin/env bash
set -euo pipefail
NS=net-ing82
[ "$(kubectl -n "$NS" get gateway echo-gw -o jsonpath='{.spec.gatewayClassName}')" = "nginx" ]
[ "$(kubectl -n "$NS" get gateway echo-gw -o jsonpath='{.spec.listeners[0].name}')" = "http" ]
[ "$(kubectl -n "$NS" get gateway echo-gw -o jsonpath='{.spec.listeners[0].protocol}')" = "HTTP" ]
[ "$(kubectl -n "$NS" get gateway echo-gw -o jsonpath='{.spec.listeners[0].port}')" = "80" ]
[ "$(kubectl -n "$NS" get gateway echo-gw -o jsonpath='{.spec.listeners[0].hostname}')" = "echo.cka.local" ]
