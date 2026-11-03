#!/usr/bin/env bash
set -euo pipefail
NS=net-ingpath
HOST=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.rules[0].host}')
[ "$HOST" = "shop.cka.local" ]
PATHP=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.rules[0].http.paths[0].path}')
[ "$PATHP" = "/shop" ]
SVC=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}')
[ "$SVC" = "shop" ]
CLASS=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.ingressClassName}')
[ "$CLASS" = "nginx" ]
exit 0
