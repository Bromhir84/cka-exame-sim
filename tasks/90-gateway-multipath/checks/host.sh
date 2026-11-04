#!/usr/bin/env bash
set -euo pipefail
NS=net-mp90
[ "$(kubectl -n "$NS" get httproute split -o jsonpath='{.spec.parentRefs[0].name}')" = "split-gw" ]
[ "$(kubectl -n "$NS" get httproute split -o jsonpath='{.spec.hostnames[0]}')" = "split.cka.local" ]
