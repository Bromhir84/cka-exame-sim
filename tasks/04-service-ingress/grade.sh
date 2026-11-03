#!/usr/bin/env bash
set -euo pipefail

NS=net-lab
TYPE=$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.type}')
[ "$TYPE" = "ClusterIP" ] || [ -z "$TYPE" ]
PORT=$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.ports[0].port}')
TARGET=$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$PORT" = "80" ]
[ "$TARGET" = "8080" ]
SEL=$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "hello" ]

HOST=$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.rules[0].host}')
[ "$HOST" = "hello.cka.local" ]
SVC=$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}')
[ "$SVC" = "hello-svc" ]
SP=$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.port.number}')
[ "$SP" = "80" ]
CLASS=$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.ingressClassName}')
[ "$CLASS" = "nginx" ]

exit 0
