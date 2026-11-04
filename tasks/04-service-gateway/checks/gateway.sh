#!/usr/bin/env bash
set -euo pipefail
NS=net-lab
[ "$(kubectl -n "$NS" get gateway hello-gw -o jsonpath='{.spec.gatewayClassName}')" = "nginx" ]
[ "$(kubectl -n "$NS" get gateway hello-gw -o jsonpath='{.spec.listeners[0].name}')" = "http" ]
[ "$(kubectl -n "$NS" get gateway hello-gw -o jsonpath='{.spec.listeners[0].protocol}')" = "HTTP" ]
[ "$(kubectl -n "$NS" get gateway hello-gw -o jsonpath='{.spec.listeners[0].port}')" = "80" ]
[ "$(kubectl -n "$NS" get gateway hello-gw -o jsonpath='{.spec.listeners[0].hostname}')" = "hello.cka.local" ]
