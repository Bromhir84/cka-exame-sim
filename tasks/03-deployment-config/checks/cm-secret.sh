#!/usr/bin/env bash
set -euo pipefail

NS=workloads-lab
kubectl -n "$NS" get cm app-config -o jsonpath='{.data.APP_ENV}' | grep -qx production
TOKEN=$(kubectl -n "$NS" get secret app-secret -o jsonpath='{.data.APP_TOKEN}' | base64 -d)
[ "$TOKEN" = "s3cr3t" ]
