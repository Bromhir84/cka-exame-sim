#!/usr/bin/env bash
set -euo pipefail
NS=ts-target
TP=$(kubectl -n "$NS" get svc echo-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "8080" ]
PORT=$(kubectl -n "$NS" get svc echo-svc -o jsonpath='{.spec.ports[0].port}')
[ "$PORT" = "80" ]
SEL=$(kubectl -n "$NS" get svc echo-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "echo" ]
exit 0
