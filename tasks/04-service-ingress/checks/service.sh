#!/usr/bin/env bash
set -euo pipefail

NS=net-lab
TYPE=$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.type}')
[ "$TYPE" = "ClusterIP" ] || [ -z "$TYPE" ]
[ "$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.ports[0].port}')" = "80" ]
[ "$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.ports[0].targetPort}')" = "8080" ]
[ "$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.selector.app}')" = "hello" ]
