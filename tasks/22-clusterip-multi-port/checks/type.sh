#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n net-multiport get svc dual-svc -o jsonpath="{.spec.type}"); [ "$TYPE" = "ClusterIP" ] || [ -z "$TYPE" ]
