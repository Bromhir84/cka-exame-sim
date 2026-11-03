#!/usr/bin/env bash
set -euo pipefail
NS=net-nodeport
TYPE=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.type}')
[ "$TYPE" = "NodePort" ]
PORT=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.ports[0].port}')
NP=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.ports[0].nodePort}')
[ "$PORT" = "80" ]
[ "$NP" = "30080" ]
SEL=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "web" ]
exit 0
