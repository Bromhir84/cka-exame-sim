#!/usr/bin/env bash
set -euo pipefail

NS=net-lab
[ "$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.rules[0].host}')" = "hello.cka.local" ]
[ "$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}')" = "hello-svc" ]
[ "$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.ingressClassName}')" = "nginx" ]
