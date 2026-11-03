#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n net-ext get svc search-ext -o jsonpath='{.spec.type}')
[ "$TYPE" = "ExternalName" ]
exit 0
