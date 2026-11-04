#!/usr/bin/env bash
set -euo pipefail
NS=net-tls86
[ "$(kubectl -n "$NS" get gateway web-gw -o jsonpath='{.spec.gatewayClassName}')" = "nginx" ]
[ "$(kubectl -n "$NS" get gateway web-gw -o jsonpath='{.spec.listeners[0].name}')" = "https" ]
[ "$(kubectl -n "$NS" get gateway web-gw -o jsonpath='{.spec.listeners[0].protocol}')" = "HTTPS" ]
[ "$(kubectl -n "$NS" get gateway web-gw -o jsonpath='{.spec.listeners[0].port}')" = "443" ]
[ "$(kubectl -n "$NS" get gateway web-gw -o jsonpath='{.spec.listeners[0].hostname}')" = "tls.cka.local" ]
[ "$(kubectl -n "$NS" get gateway web-gw -o jsonpath='{.spec.listeners[0].tls.mode}')" = "Terminate" ]
[ "$(kubectl -n "$NS" get gateway web-gw -o jsonpath='{.spec.listeners[0].tls.certificateRefs[0].name}')" = "web-tls" ]
