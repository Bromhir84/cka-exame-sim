#!/usr/bin/env bash
set -euo pipefail
REQ=$(kubectl -n stor-big get pvc big-data -o jsonpath='{.spec.resources.requests.storage}')
[ "$REQ" = "5Gi" ]
exit 0
