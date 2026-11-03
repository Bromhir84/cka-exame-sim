#!/usr/bin/env bash
set -euo pipefail
PATHS=$(kubectl -n net-mp90 get ingress split -o jsonpath='{.spec.rules[0].http.paths[*].path}')
echo "$PATHS" | grep -q '/app'
echo "$PATHS" | grep -q '/api'
SVCS=$(kubectl -n net-mp90 get ingress split -o jsonpath='{.spec.rules[0].http.paths[*].backend.service.name}')
echo "$SVCS" | grep -q app
echo "$SVCS" | grep -q api
exit 0
