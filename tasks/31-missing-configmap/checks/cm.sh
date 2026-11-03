#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-cm get cm app-settings >/dev/null
[ "$(kubectl -n ts-cm get cm app-settings -o jsonpath="{.data.mode}")" = "online" ]
