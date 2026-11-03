#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n net-ing82 get ingress echo-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}')
[ "$S" = "echo" ]
exit 0
