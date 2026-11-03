#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.type}")" = "NodePort" ]
[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.ports[0].port}")" = "80" ]
[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.ports[0].nodePort}")" = "30080" ]
