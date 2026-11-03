#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n net-ingpath get ingress shop-ing -o jsonpath="{.spec.rules[0].http.paths[0].backend.service.name}")" = "shop" ]
[ "$(kubectl -n net-ingpath get ingress shop-ing -o jsonpath="{.spec.ingressClassName}")" = "nginx" ]
