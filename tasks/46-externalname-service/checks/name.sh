#!/usr/bin/env bash
set -euo pipefail
EXT=$(kubectl -n net-ext get svc search-ext -o jsonpath='{.spec.externalName}')
[ "$EXT" = "www.example.com" ]
exit 0
