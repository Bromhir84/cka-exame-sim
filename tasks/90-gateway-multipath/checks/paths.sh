#!/usr/bin/env bash
set -euo pipefail
NS=net-mp90
JSON=$(kubectl -n "$NS" get httproute split -o json)
echo "$JSON" | grep -q '/app'
echo "$JSON" | grep -q '/api'
echo "$JSON" | grep -q '"name": "app"' || echo "$JSON" | grep -q '"name":"app"'
echo "$JSON" | grep -q '"name": "api"' || echo "$JSON" | grep -q '"name":"api"'
